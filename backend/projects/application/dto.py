from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from projects.domain.entities import Project
from projects.domain.enums import ProjectStatus
from shared.application.use_cases.base import ResponseDTO


@dataclass(frozen=True, slots=True)
class ProjectDTO(ResponseDTO):
    """Application level representation of a project."""

    id: UUID
    name: str
    description: str | None
    status: ProjectStatus
    deadline: datetime
    created_at: datetime

    @classmethod
    def from_entity(cls, project: Project) -> "ProjectDTO":
        if project.id is None:
            raise ValueError("Cannot map a project that was never persisted.")
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            deadline=project.deadline,
            created_at=project.created_at,
        )


@dataclass(frozen=True, slots=True)
class ProjectPageDTO(ResponseDTO):
    """A single page of projects together with the total number of records."""

    items: list[ProjectDTO]
    total: int
    limit: int
    offset: int
