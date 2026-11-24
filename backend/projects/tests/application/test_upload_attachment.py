from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from django.test import SimpleTestCase

from projects.application.interfaces import (
    ProjectAttachmentRepository,
    ProjectRepository,
)
from projects.application.use_cases import upload_attachment
from projects.domain.entities import Project, ProjectAttachment
from projects.domain.enums import ProjectStatus
from projects.domain.exceptions import (
    ClosedProjectException,
    InvalidProjectAttachmentException,
    ProjectNotFoundException,
)
from projects.domain.value_objects import MAX_ATTACHMENT_FILE_SIZE_BYTES
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
    created: list[dict[object, object]] = []

    @staticmethod
    def get(project_id: UUID, attachment_id: UUID) -> ProjectAttachment | None:
        return None

    @staticmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:
        return 0

    @staticmethod
    def create(actor_id: UUID, project_id: UUID, file: File) -> ProjectAttachment:
        attachment = ProjectAttachment(
            id=uuid4(),
            file=file,
            upload_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        FakeProjectAttachmentRepository.created.append(
            {
                "actor_id": actor_id,
                "project_id": project_id,
                "file": file,
                "attachment": attachment,
            }
        )
        return attachment

    @staticmethod
    def _to_entity(model: object) -> ProjectAttachment:
        raise NotImplementedError


def make_project(*, status: ProjectStatus = ProjectStatus.PLANNED) -> Project:
    now = datetime.now(timezone.utc)
    return Project(
        id=uuid4(),
        name="Project",
        description=None,
        attachments=[],
        status=status,
        deadline=now + timedelta(days=1),
        created_at=now,
    )


class UploadAttachmentUseCaseTests(SimpleTestCase):
    def setUp(self) -> None:
        FakeProjectRepository.project = make_project()
        FakeProjectAttachmentRepository.created = []
        self.use_case = upload_attachment.UseCase(
            projects=FakeProjectRepository,
            attachments=FakeProjectAttachmentRepository,
        )

    def _command(self, **overrides: object) -> upload_attachment.Command:
        data: dict[object, object] = {
            "actor_id": uuid4(),
            "project_id": FakeProjectRepository.project.id,
            "file_name": "report.pdf",
            "content": b"pdf-content",
            "content_type": "application/pdf",
            "content_size": len(b"pdf-content"),
        }
        data.update(overrides)
        return upload_attachment.Command(**data)  # type: ignore[arg-type]

    def test_uploads_attachment(self) -> None:
        response = self.use_case.execute(self._command())

        self.assertEqual(response.project_id, FakeProjectRepository.project.id)
        self.assertEqual(response.file_name, "report.pdf")
        self.assertEqual(len(FakeProjectAttachmentRepository.created), 1)

    def test_rejects_missing_project(self) -> None:
        with self.assertRaises(ProjectNotFoundException):
            self.use_case.execute(self._command(project_id=uuid4()))

    def test_rejects_closed_project(self) -> None:
        FakeProjectRepository.project = make_project(status=ProjectStatus.COMPLETED)
        self.use_case = upload_attachment.UseCase(
            projects=FakeProjectRepository,
            attachments=FakeProjectAttachmentRepository,
        )

        with self.assertRaises(ClosedProjectException):
            self.use_case.execute(
                self._command(project_id=FakeProjectRepository.project.id)
            )

    def test_rejects_disallowed_file_type(self) -> None:
        with self.assertRaises(InvalidProjectAttachmentException):
            self.use_case.execute(
                self._command(file_name="malware.exe", content=b"MZ", content_size=2)
            )

    def test_rejects_file_name_with_slashes(self) -> None:
        with self.assertRaises(InvalidProjectAttachmentException):
            self.use_case.execute(self._command(file_name="../secret.pdf"))

    def test_rejects_too_long_file_name(self) -> None:
        with self.assertRaises(InvalidProjectAttachmentException):
            self.use_case.execute(self._command(file_name="a" * 101))

    def test_rejects_file_larger_than_5mb(self) -> None:
        with self.assertRaises(InvalidProjectAttachmentException):
            self.use_case.execute(
                self._command(
                    file_name="big.pdf",
                    content=b"a" * (MAX_ATTACHMENT_FILE_SIZE_BYTES + 1),
                    content_size=MAX_ATTACHMENT_FILE_SIZE_BYTES + 1,
                )
            )
