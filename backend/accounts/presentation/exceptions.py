from typing import Final

from accounts.domain import exceptions as domain_exceptions
from rest_framework import status

EXCEPTION_MAPPER: Final[dict[BaseException, int]] = {
    domain_exceptions.InvalidEmailException: status.HTTP_400_BAD_REQUEST,
    domain_exceptions.EmailAlreadyTakenException: status.HTTP_400_BAD_REQUEST,
    domain_exceptions.WeakPasswordException: status.HTTP_400_BAD_REQUEST,
    domain_exceptions.InvalidCredentialsException: status.HTTP_401_UNAUTHORIZED,
    domain_exceptions.InvalidTokenException: status.HTTP_401_UNAUTHORIZED,
    domain_exceptions.UserNotFoundException: status.HTTP_404_NOT_FOUND,
    domain_exceptions.AccountsException: status.HTTP_400_BAD_REQUEST,
}
