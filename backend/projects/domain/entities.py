from dataclasses import dataclass
from uuid import UUID
from typing import Final
from datetime import datetime
from projects.domain.enums import ProjectStatus
from projects.domain.exceptions import (
    InvalidProjectDeadlineException,
    IllegalProjectStateTransitionException,
)
from shared.domain.entities import File

from projects.domain import exceptions

_PROJECT_STATUS_TRANSTITIONS: Final[dict[ProjectStatus, frozenset[ProjectStatus]]] = {
    ProjectStatus.PLANNED: frozenset([ProjectStatus.IN_PROGRESS]),
    ProjectStatus.IN_PROGRESS: frozenset([ProjectStatus.COMPLETED]),
    ProjectStatus.COMPLETED: frozenset([]),
}


@dataclass(frozen=True, slots=True)
class ProjectAttachment:
    id: UUID | None
    file: File
    upload_date: datetime


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID | None
    name: str
    description: str | None
    attachments: list[ProjectAttachment]
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

    def add_attachment(self, attachment: ProjectAttachment) -> ProjectAttachment:
        """Adds and returns the new attachment."""

        if self.status == ProjectStatus.COMPLETED:
            raise exceptions.ClosedProjectException(action="adding attachment")

        self.attachments.append(attachment)
        return attachment

    def get_attachment(self, id: UUID) -> ProjectAttachment:
        """Returns the attachment with the given id."""

        attachment = next((obj for obj in self.attachments if obj.id == id), None)

        if attachment is None:
            raise exceptions.ProjectAttachmentNotFoundException

        return attachment

    def delete_attachment(self, id: UUID) -> ProjectAttachment:
        "Removes and returns deleted attachment."

        if self.status == ProjectStatus.COMPLETED:
            raise exceptions.ClosedProjectException(action="deleting attachment")

        deleted_attachment = self.get_attachment(id=id)
        self.attachments.remove(deleted_attachment)

        return deleted_attachment
