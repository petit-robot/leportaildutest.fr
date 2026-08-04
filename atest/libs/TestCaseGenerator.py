"""Robot Framework pre-run modifier multiplying a test template per directory resource.

::

    robot --prerunmodifier atest/libs/TestCaseGenerator.py atest/tests/relevance.robot

The suite declares one test case, which acts as a test template:

::

    *** Test Cases ***
    Test Resource ${resource}
        Should Language Be French    ${resource}
        ...

It is replaced by one copy per Markdown file under content/directory/. Each copy keeps the body of the test template
untouched and gets the resource it audits bound to `${resource}`, so adding a resource adds a test with nothing else to
maintain. The assertions and any tags stay declared in the .robot file; only the resources come from here.

The name of the test template is templated too: the variables it embeds are resolved against the resource, so `Test
Resource ${resource}` becomes `Test Resource blogs/all4test`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from robot.api import SuiteVisitor
from robot.running.model import Keyword
from robot.variables import Variables
from robot.variables.search import search_variable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from resources import Resource, list_resources

RESOURCE_VARIABLE = "${resource}"


class TestCaseGenerator(SuiteVisitor):
    """Replace the test template of the suite by one test case per resource."""

    def __init__(self, content_root: str | None = None):
        """`content_root` overrides content/directory/, the directory read by default."""
        self._content_root = content_root

    def start_suite(self, suite):
        """Swap the test template for its copies, before the suite runs."""
        test_template = self._test_template(suite)
        if test_template is None:
            return
        suite.tests.clear()
        for resource in list_resources(self._content_root):
            suite.tests.append(self._instantiate_test(test_template, resource))

    @staticmethod
    def _test_template(suite):
        """Return the test case acting as a test template: the one with a templated name."""
        return next(
            (test for test in suite.tests if search_variable(test.name, ignore_errors=True).identifier),
            None,
        )

    def _instantiate_test(self, test_template, resource: Resource):
        """Return one copy of the test template, bound to `resource`."""
        test = test_template.deepcopy(
            name=self._name(test_template, resource),
            doc=resource.title,
            tags=[
                *test_template.tags,
                f"category:{resource.category}",
                f"resource:{resource.category_key}",
                f"status:{resource.status.lower()}",
            ],
        )
        # The body reads ${resource}, so the copy has to define it. Loading it
        # here rather than in the .robot file keeps the test free of the
        # plumbing that made it a test template in the first place.
        test.body.insert(
            0,
            Keyword(
                name="Load Resource",
                args=[resource.identifier],
                assign=[RESOURCE_VARIABLE],
            ),
        )
        return test

    @staticmethod
    def _name(test_template, resource: Resource) -> str:
        """Fill the resource into the name of the test template, Robot's own way.

        Going through Robot's variable replacement rather than a plain string substitution means `${resource.title}`
        names its title, exactly as it would inside the test body.
        """
        variables = Variables()
        variables[RESOURCE_VARIABLE] = resource
        return variables.replace_string(test_template.name, ignore_errors=True)
