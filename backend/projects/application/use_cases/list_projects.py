from dataclasses import dataclass

from projects.application.dto import ProjectDTO, ProjectPageDTO
from projects.application.interfaces import ProjectRepository
from shared.application.use_cases.base import Command, UseCase


@dataclass(frozen=True, slots=True)
class ListProjectsCommand(Command):
    limit: int
    offset: int


class ListProjectsUseCase(UseCase):
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, command: ListProjectsCommand) -> ProjectPageDTO:
        pass
