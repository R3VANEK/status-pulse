from django.test import SimpleTestCase
from datetime import timedelta
from django.utils import timezone
from projects.domain.enums import ProjectStatus
from projects.domain.entities import Project
from projects.domain.exceptions import (
    IllegalProjectStateTransitionException,
    InvalidProjectDeadlineException,
)


class ProjectTests(SimpleTestCase):
    def test_project_completion(self) -> None:
        invalid_statuses = [
            value for value in ProjectStatus if value != ProjectStatus.IN_PROGRESS
        ]
        for status in invalid_statuses:
            with self.subTest(status=status):
                project = Project(
                    id=None,
                    name="test",
                    description=None,
                    deadline=timezone.now() + timedelta(days=1),
                    created_at=timezone.now(),
                    status=status,
                )

                with self.assertRaises(IllegalProjectStateTransitionException):
                    project.complete()

        project = Project(
            id=None,
            name="test",
            description=None,
            deadline=timezone.now() + timedelta(days=1),
            created_at=timezone.now(),
            status=ProjectStatus.IN_PROGRESS,
        )

        project.complete()

        self.assertEqual(project.status, ProjectStatus.COMPLETED)

    def test_project_start(self) -> None:
        invalid_statuses = [
            value for value in ProjectStatus if value != ProjectStatus.PLANNED
        ]
        for status in invalid_statuses:
            with self.subTest(status=status):
                project = Project(
                    id=None,
                    name="test",
                    description=None,
                    deadline=timezone.now() + timedelta(days=1),
                    created_at=timezone.now(),
                    status=status,
                )

                with self.assertRaises(IllegalProjectStateTransitionException):
                    project.start()

        project = Project(
            id=None,
            name="test",
            description=None,
            deadline=timezone.now() + timedelta(days=1),
            created_at=timezone.now(),
            status=ProjectStatus.PLANNED,
        )

        project.start()

        self.assertEqual(project.status, ProjectStatus.IN_PROGRESS)

    def test_project_deadline(self) -> None:

        now = timezone.now()

        with self.assertRaises(InvalidProjectDeadlineException):
            project = Project(  # noqa: F841
                id=None,
                name="test",
                description=None,
                status=ProjectStatus.PLANNED,
                created_at=now,
                deadline=now,
            )

        with self.assertRaises(InvalidProjectDeadlineException):
            project = Project(  # noqa: F841
                id=None,
                name="test",
                description=None,
                status=ProjectStatus.PLANNED,
                created_at=now,
                deadline=now - timedelta(days=1),
            )
