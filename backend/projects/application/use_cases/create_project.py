from dataclasses import dataclass
from datetime import datetime, timezone

from projects.application.dto import ProjectDTO
from projects.application.interfaces import ProjectRepository
from projects.domain.entities import Project
from projects.domain.enums import ProjectStatus
from shared.application.use_cases.base import Command, UseCase


@dataclass(frozen=True, slots=True)
class CreateProjectCommand(Command):
    name: str
    description: str | None
    deadline: datetime


class CreateProjectUseCase(UseCase):
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, command: CreateProjectCommand) -> ProjectDTO:
        pass
