from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from projects.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from projects.domain.enums import ProjectStatus
from projects.domain.exceptions import InvalidProjectDeadlineException
from projects.tests.application.fakes import InMemoryProjectRepository


class CreateProjectTests(SimpleTestCase):
    def setUp(self) -> None:
        self.projects = InMemoryProjectRepository()
        self.use_case = CreateProjectUseCase(projects=self.projects)

    def test_creates_planned_project(self) -> None:
        deadline = datetime.now(timezone.utc) + timedelta(days=7)

        project = self.use_case.execute(
            CreateProjectCommand(
                name="Status pulse",
                description="Project that pings us",
                deadline=deadline,
            )
        )

        self.assertEqual(project.name, "Status pulse")
        self.assertEqual(project.description, "Project that pings us")
        self.assertEqual(project.status, ProjectStatus.PLANNED)
        self.assertEqual(project.deadline, deadline)
        self.assertIsNotNone(project.id)

    def test_stores_the_project(self) -> None:
        deadline = datetime.now(timezone.utc) + timedelta(days=7)

        project = self.use_case.execute(
            CreateProjectCommand(
                name="Status pulse", description=None, deadline=deadline
            )
        )

        self.assertEqual(len(self.projects.projects), 1)
        self.assertEqual(self.projects.projects[0].id, project.id)

    def test_description_is_optional(self) -> None:
        deadline = datetime.now(timezone.utc) + timedelta(days=7)

        project = self.use_case.execute(
            CreateProjectCommand(
                name="No description", description=None, deadline=deadline
            )
        )

        self.assertIsNone(project.description)

    def test_rejects_deadline_in_the_past(self) -> None:
        deadline = datetime.now(timezone.utc) - timedelta(days=1)

        with self.assertRaises(InvalidProjectDeadlineException):
            self.use_case.execute(
                CreateProjectCommand(
                    name="Late project", description=None, deadline=deadline
                )
            )

        self.assertEqual(self.projects.projects, [])
