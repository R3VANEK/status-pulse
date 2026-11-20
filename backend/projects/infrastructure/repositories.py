from projects.infrastructure import models
from projects.domain import entities
from projects.application.interfaces import ProjectAttachmentRepository
from uuid import UUID
from shared.domain.entities import File
from projects.domain.enums import ProjectStatus
from shared.infrastructure.repositories import (
    TooManyRecordsReturnedException,
    RepositoryException,
)
from projects.application.interfaces import ProjectRepository
from shared.infrastructure.repositories import RepositoryExceptionWrapper


class DjangoProjectRepository(ProjectRepository):

    @staticmethod
    def get(actor_id: UUID, project_id: UUID) -> entities.Project | None:  # type: ignore
        """get project within actor scope"""

        projects = models.Project.objects.filter(id=project_id)

        if projects is None or len(projects) <= 0:
            return None

        if len(projects) != 1:
            raise TooManyRecordsReturnedException()

        project = projects[0]

        return DjangoProjectRepository._to_entity(model=project)

    @staticmethod
    def _to_entity(model: models.Project) -> entities.Project:
        """Parse orm-like object to domain entity"""

        model_attachments: list[models.ProjectAttachment] = list(model.attachments.all())  # type: ignore
        entity_attachments: list[entities.ProjectAttachment] = []

        for attachment in model_attachments:
            entity_attachments.append(
                DjangoProjectAttachmentRepository._to_entity(attachment)
            )

        return entities.Project(
            id=model.id,
            name=model.name,
            description=model.description,
            status=ProjectStatus(model.status),
            deadline=model.deadline,
            created_at=model.created_at,
            attachments=entity_attachments,
        )


class DjangoProjectAttachmentRepository(ProjectAttachmentRepository):

    @staticmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:  # type: ignore
        """delete attachment by its id and project id and return number of deleted rows"""

        # TODO: complete here the query for check user in project
        return models.ProjectAttachment.objects.filter(
            id=attachment_id, project_id=project_id
        ).delete()[0]

    @staticmethod
    def _to_entity(model: models.ProjectAttachment) -> entities.ProjectAttachment:
        """Parse orm-like object to domain entity"""
        return entities.ProjectAttachment(
            id=model.id,
            upload_date=model.upload_date,
            file=File(
                name=model.file_name,
                content=model.file.file,
                content_type=model.content_type,
                content_size=model.content_size,
            ),
        )
