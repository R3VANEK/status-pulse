from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from django.test import SimpleTestCase

from projects.application.interfaces import (
    ProjectAttachmentRepository,
    ProjectRepository,
)
from projects.application.use_cases import download_attachment
from projects.domain.entities import Project, ProjectAttachment
from projects.domain.enums import ProjectStatus
from projects.domain.exceptions import (
    ProjectAttachmentNotFoundException,
    ProjectNotFoundException,
)
from shared.domain.entities import File


class FakeProjectRepository(ProjectRepository):
    project: Project | None = None

    @staticmethod
    def get(actor_id: UUID, project_id: UUID) -> Project | None:
        project = FakeProjectRepository.project
        if project is None or project.id != project_id:
            return None
        return project

    @staticmethod
    def _to_entity(model: object) -> Project:
        raise NotImplementedError


class FakeProjectAttachmentRepository(ProjectAttachmentRepository):
    attachments: dict[tuple[UUID, UUID], ProjectAttachment] = {}

    @staticmethod
    def get(project_id: UUID, attachment_id: UUID) -> ProjectAttachment | None:
        return FakeProjectAttachmentRepository.attachments.get(
            (project_id, attachment_id)
        )

    @staticmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:
        return 0

    @staticmethod
    def create(actor_id: UUID, project_id: UUID, file: File) -> ProjectAttachment:
        raise NotImplementedError

    @staticmethod
    def _to_entity(model: object) -> ProjectAttachment:
        raise NotImplementedError


def make_project(attachments: list[ProjectAttachment] | None = None) -> Project:
    now = datetime.now(timezone.utc)
    return Project(
        id=uuid4(),
        name="Project",
        description=None,
        attachments=attachments or [],
        status=ProjectStatus.PLANNED,
        deadline=now + timedelta(days=1),
        created_at=now,
    )


def make_attachment() -> ProjectAttachment:
    return ProjectAttachment(
        id=uuid4(),
        file=File(
            name="report.txt",
            content=b"attachment content",
            content_type="text/plain",
            content_size=len(b"attachment content"),
        ),
        upload_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class DownloadAttachmentUseCaseTests(SimpleTestCase):
    def setUp(self) -> None:
        self.attachment = make_attachment()
        self.project = make_project(attachments=[self.attachment])
        FakeProjectRepository.project = self.project
        FakeProjectAttachmentRepository.attachments = {
            (self.project.id, self.attachment.id): self.attachment  # type: ignore[dict-item]
        }
        self.use_case = download_attachment.UseCase(
            projects=FakeProjectRepository,
            attachments=FakeProjectAttachmentRepository,
        )

    def _command(self, **overrides: object) -> download_attachment.Command:
        data: dict[object, object] = {
            "actor_id": uuid4(),
            "project_id": self.project.id,
            "attachment_id": self.attachment.id,
        }
        data.update(overrides)
        return download_attachment.Command(**data)  # type: ignore[arg-type]

    def test_returns_attachment_file(self) -> None:
        response = self.use_case.execute(self._command())

        self.assertEqual(response.file.name, "report.txt")
        self.assertEqual(response.file.content, b"attachment content")
        self.assertEqual(response.file.content_type, "text/plain")

    def test_rejects_missing_project(self) -> None:
        with self.assertRaises(ProjectNotFoundException):
            self.use_case.execute(self._command(project_id=uuid4()))

    def test_rejects_attachment_not_in_project(self) -> None:
        empty_project = make_project()
        FakeProjectRepository.project = empty_project

        with self.assertRaises(ProjectAttachmentNotFoundException):
            self.use_case.execute(self._command(project_id=empty_project.id))

    def test_rejects_missing_stored_attachment(self) -> None:
        FakeProjectAttachmentRepository.attachments = {}

        with self.assertRaises(ProjectAttachmentNotFoundException):
            self.use_case.execute(self._command())
