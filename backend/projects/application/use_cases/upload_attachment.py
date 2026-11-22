from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from projects.application.interfaces import (
    ProjectAttachmentRepository,
    ProjectRepository,
)
from projects.domain.entities import ProjectAttachment
from projects.domain.exceptions import ProjectNotFoundException
from projects.domain.value_objects import AttachmentFile
from shared.application.use_cases.base import (
    Command as BaseCommand,
    ResponseDTO as BaseResponseDTO,
    UseCase as BaseUseCase,
)
from shared.domain.entities import File


@dataclass(frozen=True, slots=True)
class Command(BaseCommand):
    actor_id: UUID
    project_id: UUID
    file_name: str
    content: bytes
    content_type: str
    content_size: int


@dataclass(frozen=True, slots=True)
class ResponseDTO(BaseResponseDTO):
    id: UUID
    project_id: UUID
    file_name: str
    upload_date: datetime


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

        validated_file = AttachmentFile(
            name=command.file_name,
            content=command.content,
            content_type=command.content_type,
            content_size=len(command.content),
        )
        file = File(
            name=validated_file.name,
            content=validated_file.content,
            content_type=validated_file.content_type,
            content_size=validated_file.content_size,
        )

        project.add_attachment(
            ProjectAttachment(
                id=None,
                file=file,
                upload_date=datetime.now(timezone.utc),
            )
        )

        attachment = self._attachments.create(
            actor_id=command.actor_id,
            project_id=command.project_id,
            file=file,
        )

        if attachment.id is None:
            raise RuntimeError()

        return ResponseDTO(
            id=attachment.id,
            project_id=command.project_id,
            file_name=attachment.file.name,
            upload_date=attachment.upload_date,
        )
