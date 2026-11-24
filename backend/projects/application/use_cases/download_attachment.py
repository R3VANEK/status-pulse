from dataclasses import dataclass
from uuid import UUID

from shared.application.use_cases.base import (
    Command as BaseCommand,
    ResponseDTO as BaseResponseDTO,
    UseCase as BaseUseCase,
)
from shared.domain.entities import File

from projects.application.interfaces import (
    ProjectAttachmentRepository,
    ProjectRepository,
)
from projects.domain.exceptions import (
    ProjectAttachmentNotFoundException,
    ProjectNotFoundException,
)


@dataclass(frozen=True, slots=True)
class Command(BaseCommand):
    actor_id: UUID
    project_id: UUID
    attachment_id: UUID


@dataclass(frozen=True, slots=True)
class ResponseDTO(BaseResponseDTO):
    file: File


class UseCase(BaseUseCase):
    def __init__(
        self,
        attachments: type[ProjectAttachmentRepository],
        projects: type[ProjectRepository],
    ) -> None:
        self._attachments = attachments
        self._projects = projects

    def execute(self, command: Command) -> ResponseDTO:
        project = self._projects.get(
            actor_id=command.actor_id, project_id=command.project_id
        )

        if project is None:
            raise ProjectNotFoundException()

        attachment = project.get_attachment(id=command.attachment_id)

        if attachment.id is None:
            raise RuntimeError()

        stored_attachment = self._attachments.get(
            project_id=command.project_id,
            attachment_id=attachment.id,
        )

        if stored_attachment is None:
            raise ProjectAttachmentNotFoundException()

        return ResponseDTO(file=stored_attachment.file)
