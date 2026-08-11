"""Manage the audit of the directory resources by an AI agent."""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from robot.api import SkipExecution, logger
from robot.api.deco import keyword, library

sys.path.insert(0, str(Path(__file__).resolve().parent))

import resources
from resources import Resource

DEFAULT_MODEL = "mistral-large-latest"
PAGE_EXCERPT_CHARS = 6000
HTTP_TIMEOUT = 20
HTTP_HEADERS = {
    "User-Agent": "LePortailDuTestAgent/1.0 (relevance audit)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
# Pinned so two runs on unchanged inputs give the same verdict.
RANDOM_SEED = 20260802

AGENT_INSTRUCTIONS = """\
You audit leportaildutest.fr, a directory of French-language resources about
software testing and quality engineering.

For each resource you receive its declared title, link and description, plus an
extract of the page fetched from that link. Judge the resource behind the link,
never the declaration itself: a French description may perfectly well point to
an English website, and saying so is the whole point of the audit.

Topic, language, pricing and categories are decided from the extract alone.
Never search for them.

A resource is paid when reaching its content costs money: a price, a paid
subscription, a paying membership. Having to create a free account is not a
payment: a newsletter published on LinkedIn is free, even though reading it
requires being signed in to LinkedIn.

Only the last publication date may need `web_search`, and only when the extract
carries no dated item. When it carries one, take the most recent date it shows
and search nothing.

When you do web search, you get one query, restricted to the resource's own domain
and aimed at its latest article, episode, issue or event. Allow yourself a
second  web search only if the first returned nothing attributable to the resource.
If the second result fails, it means last publication date is `unknown`.
Don't do a third web search.

Whether the resource is still running is a separate judgement, answered even
when its last publication date stays `unknown`: an announced next episode, a
coming event, a schedule still being kept, a forum still being posted to are
all activity. An abandoned page, a parked domain or a link leading nowhere is
not. Decide it from what you observe, not from the date you managed to find.

Report what you observe, not what you assume is expected. Be terse: one factual
sentence per justification.
"""

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "topic_ok": {
            "type": "boolean",
            "description": "True if the resource is about software testing or quality engineering.",
        },
        "topic_reason": {"type": "string"},
        "language_code": {
            "type": "string",
            "description": "ISO 639-1 code of the language the resource publishes in, e.g. 'fr'.",
        },
        "language_reason": {"type": "string"},
        "is_paid": {
            "type": "boolean",
            "description": "True if reaching the main content costs money. A free account is not a payment.",
        },
        "pricing_reason": {"type": "string"},
        "last_publication": {
            "type": "string",
            "description": "Date of the most recent publication as YYYY-MM-DD or 'unknown'.",
        },
        "is_active": {
            "type": "boolean",
            "description": "True if the resource is still running, whatever its last publication date.",
        },
        "is_discontinued": {
            "type": "boolean",
            "description": "True if the resource is gone, or announces it has stopped for good.",
        },
        "activity_reason": {"type": "string"},
        "tags": {
            "type": "array",
            "description": "Every category that fits the resource, taken from the allowed list.",
            "items": {"type": "string"},
        },
        "tags_reason": {"type": "string"},
    },
    "required": [
        "topic_ok",
        "topic_reason",
        "language_code",
        "language_reason",
        "is_paid",
        "pricing_reason",
        "last_publication",
        "is_active",
        "is_discontinued",
        "activity_reason",
        "tags",
        "tags_reason",
    ],
    "additionalProperties": False,
}


@library(scope="GLOBAL", version="1.0.0")
class RelevanceAuditAgent:
    """Keywords reading the directory and asking the agent what it makes of a resource."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        content_root: str | None = None,
        agent_id: str | None = None,
    ):
        """`agent_id` reuses an existing agent instead of creating one."""
        self._model = model
        self._content_root = content_root
        self._client = None
        self._agent_id = agent_id
        self._verdicts: dict[str, dict] = {}

    # -- Resources ---------------------------------------------------------

    @keyword("Load Resource")
    def load(self, identifier: str) -> Resource:
        """Return the resource named `identifier`, for instance, `blogs/all4test`."""
        return resources.load_resource(identifier, self._content_root)

    @staticmethod
    @keyword("Get Resource Categories")
    def get_resource_categories() -> dict[str, str]:
        """Return the category keys the site knows about, mapped to their description."""
        return resources.get_resource_categories()

    # -- The verdict ------------------------------------------------------

    @keyword("Get Resource Verdict")
    def get_resource_verdict(self, resource: Resource) -> dict:
        """Return what the agent makes of the resource, one field per audited criterion."""
        if resource.identifier not in self._verdicts:
            self._verdicts[resource.identifier] = self._ask_agent(resource)
            logger.info(
                f"Verdict for {resource.identifier}:\n"
                f"{json.dumps(self._verdicts[resource.identifier], indent=2, ensure_ascii=False)}"
            )
        return self._verdicts[resource.identifier]["verdict"]

    # -- The agent --------------------------------------------------------

    def _ask_agent(self, resource: Resource) -> dict:
        """Ask the agent what it finds on the resource."""
        client = self._agent_provider_client()
        page = self._fetch_page(resource.link)
        prompt = self._create_prompt(resource, page)
        response = client.beta.conversations.start(
            agent_id=self._ensure_agent(),
            inputs=prompt,
            store=False,
        )
        answer, sources = self._read_agent_answer(response)
        return {
            "identifier": resource.identifier,
            "link": resource.link,
            "model": self._model,
            "generated_at": datetime.now(UTC).isoformat(),
            "page": {"status": page["status"], "final_url": page["final_url"], "error": page["error"]},
            "sources": sources,
            "verdict": json.loads(answer),
        }

    def _agent_provider_client(self):
        """Return the agent provider client, creating it if not ever instantiated."""
        if self._client is None:
            api_key = os.environ.get("AGENT_API_KEY")
            if not api_key:
                raise SkipExecution("AGENT_API_KEY is not set")  # ruff: ignore[raise-vanilla-args]
            # Imported here so the library still loads without mistralai installed,
            # which is what makes the skip above reachable.
            from mistralai.client import Mistral  # ruff: ignore[import-outside-top-level]

            self._client = Mistral(api_key=api_key)
        return self._client

    def _ensure_agent(self) -> str:
        """Ensure the agent exists, creating it if needed. Return its ID."""
        if self._agent_id is None:
            # Sampling and output shape belong to the agent: a conversation
            # started from an `agent_id` is not allowed to carry them itself.
            agent = self._agent_provider_client().beta.agents.create(
                model=self._model,
                name="leportaildutest relevance auditor",
                description="Audits the directory resources of leportaildutest.fr.",
                instructions=AGENT_INSTRUCTIONS,
                tools=[{"type": "web_search"}],
                completion_args={
                    "temperature": 0,
                    "random_seed": RANDOM_SEED,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "resource_verdict",
                            "schema": VERDICT_SCHEMA,
                            "strict": True,
                        },
                    },
                },
            )
            self._agent_id = agent.id
            logger.info(f"Created agent {self._agent_id}")
        else:
            logger.info(f"Reusing agent {self._agent_id}")
        return self._agent_id

    @staticmethod
    def _create_prompt(resource: Resource, page: dict) -> str:
        """Create the prompt for the agent, including the resource's details and the fetched page."""
        vocabulary = "\n".join(f"- {key}: {text}" for key, text in resources.get_resource_categories().items())
        if page["error"]:
            fetched = f"The page could not be fetched: {page['error']}"
        else:
            fetched = (
                f"HTTP {page['status']} from {page['final_url']}\n\n{page['text']}"
                if page["text"]
                else f"HTTP {page['status']} from {page['final_url']}, empty body"
            )
        return f"""\
Today is {datetime.now(UTC).date().isoformat()}.

Directory resource
  title: {resource.title}
  link: {resource.link}
  description: {resource.description}

Allowed categories
{vocabulary}

Extract of the fetched page
{fetched}
"""

    @staticmethod
    def _fetch_page(url: str) -> dict:
        """Fetch the resource page. Avoid to use costly web search done by the agent."""
        try:
            response = requests.get(
                url,
                headers=HTTP_HEADERS,
                timeout=HTTP_TIMEOUT,
                allow_redirects=True,
            )
        except requests.RequestException as error:
            return {"status": None, "final_url": url, "text": "", "error": str(error)}
        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())
        return {
            "status": response.status_code,
            "final_url": str(response.url),
            "text": text[:PAGE_EXCERPT_CHARS],
            "error": None,
        }

    @staticmethod
    def _read_agent_answer(response) -> tuple[str, list[str]]:
        """Return the agent's answer, plus the URLs `web_search` cited along the way."""
        answer, sources = [], []
        for entry in response.outputs:
            logger.debug(f"Agent output entry:\n{entry}")
            if getattr(entry, "type", None) != "message.output":
                continue
            content = entry.content
            if isinstance(content, str):
                answer.append(content)
                continue
            for chunk in content:
                kind = getattr(chunk, "type", None)
                if kind == "text":
                    answer.append(chunk.text)
                elif kind == "tool_reference":
                    sources.append(getattr(chunk, "url", "") or "")
        return "".join(answer), list(dict.fromkeys(url for url in sources if url))
