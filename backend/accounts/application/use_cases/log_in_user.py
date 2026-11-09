from dataclasses import dataclass

from accounts.application.interfaces import TokenPair, TokenService, UserRepository
from accounts.domain.exceptions import (
    InvalidCredentialsException,
    InvalidEmailException,
)
from accounts.domain.value_objects import Email
from shared.application.use_cases.base import Command, UseCase


@dataclass(frozen=True, slots=True)
class LoginUserCommand(Command):
    email: str
    password: str


class LoginUserUseCase(UseCase):
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    def execute(self, command: LoginUserCommand) -> TokenPair:
        try:
            email = Email(command.email)
        except InvalidEmailException:
            # Do not reveal which part was wrong.
            raise InvalidCredentialsException() from None

        user = self._users.get_by_credentials(email, command.password)
        if user is None or not user.is_active:
            raise InvalidCredentialsException()

        return self._tokens.issue_for(user)
