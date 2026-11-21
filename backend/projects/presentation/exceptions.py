from projects.domain import exceptions as domain_exceptions
from typing import Final
from rest_framework import status

EXCEPTION_MAPPER: Final[dict[BaseException, int]] = {
    domain_exceptions.ProjectNotFoundException: status.HTTP_404_NOT_FOUND,
    domain_exceptions.ClosedProjectException: status.HTTP_409_CONFLICT,
    domain_exceptions.IllegalProjectStateTransitionException: status.HTTP_409_CONFLICT,
    domain_exceptions.InvalidProjectDeadlineException: status.HTTP_400_BAD_REQUEST,
    domain_exceptions.ProjectAttachmentNotFoundException: status.HTTP_404_NOT_FOUND,
}
