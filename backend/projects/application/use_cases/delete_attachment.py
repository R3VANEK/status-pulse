from dataclasses import dataclass
from uuid import UUID

from projects.domain.exceptions import ProjectNotFoundException

from shared.application.use_cases.base import (
    Command as BaseCommand,
    UseCase as BaseUseCase,
    ResponseDTO as BaseResponseDTO,
)

from projects.application.interfaces import (
    ProjectAttachmentRepository,
    ProjectRepository,
)


@dataclass(frozen=True, slots=True)
class Command(BaseCommand):
    actor_id: UUID
    project_id: UUID
    attachment_id: UUID


@dataclass(frozen=True, slots=True)
class ResponseDTO(BaseResponseDTO):
    objects_deleted_count: int


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

        attachment_to_delete = project.delete_attachment(id=command.attachment_id)

        if attachment_to_delete.id is None or project.id is None:
            raise RuntimeError()

        objects_deleted_count = self._attachments.delete(
            actor_id=command.actor_id,
            project_id=project.id,
            attachment_id=attachment_to_delete.id,
        )

        return ResponseDTO(objects_deleted_count=objects_deleted_count)
