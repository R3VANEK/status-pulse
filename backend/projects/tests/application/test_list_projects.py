from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from projects.application.use_cases.list_projects import (
    ListProjectsCommand,
    ListProjectsUseCase,
)
from projects.domain.entities import Project
from projects.domain.enums import ProjectStatus
from projects.tests.application.fakes import InMemoryProjectRepository


class ListProjectsTests(SimpleTestCase):
    def setUp(self) -> None:
        self.projects = InMemoryProjectRepository()
        self.use_case = ListProjectsUseCase(projects=self.projects)
        for index in range(5):
            self.projects.create(
                Project(
                    id=None,
                    name=f"Project {index}",
                    description=None,
                    status=ProjectStatus.PLANNED,
                    deadline=datetime.now(timezone.utc) + timedelta(days=7),
                    created_at=datetime.now(timezone.utc),
                )
            )

    def test_returns_all_projects_when_the_limit_is_high_enough(self) -> None:
        page = self.use_case.execute(ListProjectsCommand(limit=10, offset=0))

        self.assertEqual(page.total, 5)
        self.assertEqual(len(page.items), 5)
        self.assertEqual(page.limit, 10)
        self.assertEqual(page.offset, 0)

    def test_applies_limit_and_offset(self) -> None:
        page = self.use_case.execute(ListProjectsCommand(limit=2, offset=1))

        self.assertEqual([item.name for item in page.items], ["Project 1", "Project 2"])
        self.assertEqual(page.total, 5)
        self.assertEqual(page.limit, 2)
        self.assertEqual(page.offset, 1)

    def test_reports_the_total_number_of_projects(self) -> None:
        page = self.use_case.execute(ListProjectsCommand(limit=1, offset=0))

        self.assertEqual(page.total, 5)
        self.assertEqual(len(page.items), 1)

    def test_returns_empty_page_when_the_offset_is_beyond_the_end(self) -> None:
        page = self.use_case.execute(ListProjectsCommand(limit=2, offset=10))

        self.assertEqual(page.items, [])
        self.assertEqual(page.total, 5)
