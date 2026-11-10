from dataclasses import dataclass
from uuid import UUID
from typing import Final
from datetime import datetime
from projects.domain.enums import ProjectStatus
from projects.domain.exceptions import (
    InvalidProjectDeadlineException,
    IllegalProjectStateTransitionException,
)

_PROJECT_STATUS_TRANSTITIONS: Final[dict[ProjectStatus, frozenset[ProjectStatus]]] = {
    ProjectStatus.PLANNED: frozenset([ProjectStatus.IN_PROGRESS]),
    ProjectStatus.IN_PROGRESS: frozenset([ProjectStatus.COMPLETED]),
    ProjectStatus.COMPLETED: frozenset([]),
}


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID | None
    name: str
    description: str | None
    status: ProjectStatus
    deadline: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        if self.deadline <= self.created_at:
            raise InvalidProjectDeadlineException(
                deadline=self.deadline, created_at=self.created_at
            )

    def _transition_to_status(self, desired_status: ProjectStatus) -> None:
        if desired_status not in _PROJECT_STATUS_TRANSTITIONS[self.status]:
            raise IllegalProjectStateTransitionException(
                current_status=self.status,
                desired_status=desired_status,
            )
        object.__setattr__(self, "status", desired_status)

    def complete(self) -> None:
        self._transition_to_status(desired_status=ProjectStatus.COMPLETED)

    def start(self) -> None:
        self._transition_to_status(desired_status=ProjectStatus.IN_PROGRESS)
