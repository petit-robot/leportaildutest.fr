"""Access to the directory resources stored as Markdown files under content/directory/.

This is the single source of truth shared by the Robot Framework library and the pre-run test case generator, so both
agree on what a resource is and how many there are.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_ROOT = REPO_ROOT / "content" / "directory"
SETTINGS_FILE = REPO_ROOT / "site" / "src" / "config" / "settings.toml"

ACTIVE = "Active"
INACTIVE = "Inactive"
CLOSED = "Closed"

# The frontmatter omits `status` for the nominal case, see the field table in README.md.
_STATUSES = {None: ACTIVE, "inactive": INACTIVE, "closed": CLOSED}


@dataclass(frozen=True)
class Resource:
    """One resource of the directory, as declared in its Markdown frontmatter."""

    identifier: str  # "blogs/all4test", also the site route
    category: str  # A category is the "main" tag
    slug: str
    title: str
    link: str
    description: str
    tags: list[str]  # If a resource can be linked to multiple categories, use tags
    paid: bool
    status: str  # Active | Inactive | Closed
    path: Path

    @property
    def category_key(self) -> str:
        """Identifier without a slash, so it can be used as a Robot tag."""
        return f"{self.category}-{self.slug}"

    def __str__(self) -> str:
        """Print the resource as its identifier, the way the Robot log names it."""
        return self.identifier


def _parse(path: Path) -> Resource:
    """Return the Resource object declared in the Markdown file at `path`."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path} has no YAML frontmatter")  # ruff: ignore[raise-vanilla-args]
    _, frontmatter, _ = text.split("---", 2)
    data = yaml.safe_load(frontmatter) or {}

    status = data.get("status")
    if status not in _STATUSES:
        raise ValueError(f"{path} declares an unknown status {status!r}")  # ruff: ignore[raise-vanilla-args]

    return Resource(
        identifier=f"{path.parent.name}/{path.stem}",
        category=path.parent.name,
        slug=path.stem,
        title=data["title"],
        link=data["link"],
        description=data.get("description", ""),
        tags=list(data.get("tags", [])),
        paid=bool(data.get("paid", False)),
        status=_STATUSES[status],
        path=path,
    )


def list_resources(content_root: Path | str | None = None) -> list[Resource]:
    """List every resource found under `content_root`, sorted by identifier."""
    root = Path(content_root) if content_root else DEFAULT_CONTENT_ROOT
    resources = [_parse(path) for path in root.rglob("*.md")]
    return sorted(resources, key=lambda resource: resource.identifier)


def load_resource(identifier: str, content_root: Path | str | None = None) -> Resource:
    """Return the resource named `identifier`, for instance "blogs/all4test"."""
    root = Path(content_root) if content_root else DEFAULT_CONTENT_ROOT
    path = root / f"{identifier}.md"
    if not path.is_file():
        raise ValueError(f"No resource named {identifier!r} under {root}")  # ruff: ignore[raise-vanilla-args]
    return _parse(path)


def get_resource_categories(settings_file: Path | str | None = None) -> dict[str, str]:
    """Return the category keys the site knows about, mapped to their description.

    Read from the site configuration rather than hardcoded, so the agent is always asked to classify within the
    categories the site actually offers.
    """
    path = Path(settings_file) if settings_file else SETTINGS_FILE
    settings = tomllib.loads(path.read_text(encoding="utf-8"))
    return {tag["key"]: tag["description"] for tag in settings["directoryData"]["tags"]}
