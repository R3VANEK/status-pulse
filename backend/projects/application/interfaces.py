from abc import ABC, abstractmethod
from uuid import UUID
from projects.domain.entities import ProjectAttachment, Project
from shared.domain.entities import File
from typing import Any
from shared.infrastructure.repositories import RepositoryExceptionWrapper


class ProjectAttachmentRepository(ABC, metaclass=RepositoryExceptionWrapper):
    @staticmethod
    @abstractmethod
    def get(project_id: UUID, attachment_id: UUID) -> ProjectAttachment | None:
        """get attachment by project id and its id"""

    @staticmethod
    @abstractmethod
    def delete(actor_id: UUID, project_id: UUID, attachment_id: UUID) -> int:
        """delete attachment by its id and project id and return number of deleted rows"""

    @staticmethod
    @abstractmethod
    def create(actor_id: UUID, project_id: UUID, file: File) -> ProjectAttachment:
        """create attachment for a project"""

    @staticmethod
    @abstractmethod
    def _to_entity(model: Any) -> ProjectAttachment:
        """Parse orm-like object to domain entity"""


class ProjectRepository(ABC, metaclass=RepositoryExceptionWrapper):
    @staticmethod
    @abstractmethod
    def get(actor_id: UUID, project_id: UUID) -> Project | None:
        """get project within actor scope"""

    @staticmethod
    @abstractmethod
    def _to_entity(model: Any) -> Project:
        """Parse orm-like object to domain entity"""
