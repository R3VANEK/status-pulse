from abc import ABC, abstractmethod

from projects.domain.entities import Project


class ProjectRepository(ABC):
    @abstractmethod
    def create(self, project: Project) -> Project:
        """Persist a new project and return it with the assigned id."""

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[Project]:
        """Return a slice of the stored projects, newest first."""

    @abstractmethod
    def count(self) -> int:
        """Return the total number of stored projects."""
