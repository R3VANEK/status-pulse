from datetime import datetime
from shared.domain.exceptions import DomainException
from projects.domain.enums import ProjectStatus


class InvalidProjectDeadlineException(DomainException):
    def __init__(self, deadline: datetime, creation_time: datetime) -> None:
        super().__init__(
            f"Project's deadline of {deadline} can't be earlier than its created_at timestamp {creation_time}"
        )


class IllegalProjectStateTransitionException(DomainException):
    def __init__(
        self, current_status: ProjectStatus, desired_status: ProjectStatus
    ) -> None:
        super().__init__(
            f"Transition from project's current status of {current_status} to {desired_status} is illegal"
        )
