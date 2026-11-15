"""In-memory implementations of application interfaces, used by unit tests."""

from dataclasses import replace
from uuid import uuid4

from projects.application.interfaces import ProjectRepository
from projects.domain.entities import Project


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        self.projects: list[Project] = []

    def create(self, project: Project) -> Project:
        stored = replace(project, id=uuid4())
        self.projects.append(stored)
        return stored

    def list(self, limit: int, offset: int) -> list[Project]:
        return self.projects[offset : offset + limit]

    def count(self) -> int:
        return len(self.projects)
