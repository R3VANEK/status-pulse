from accounts.application.interfaces import (
    PasswordPolicy,
    TokenPair,
    TokenService,
    UserRepository,
)
from accounts.domain.exceptions import EmailAlreadyTakenException
from accounts.domain.value_objects import Email
from shared.application.use_cases.base import Command, UseCase
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterUserCommand(Command):
    email: str
    password: str


class RegisterUserUseCase(UseCase):
    def __init__(
        self,
        users: UserRepository,
        password_policy: PasswordPolicy,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._password_policy = password_policy
        self._tokens = tokens

    def execute(self, command: RegisterUserCommand) -> TokenPair:
        email = Email(command.email)  # raises InvalidEmailException

        if self._users.exists_with_email(email):
            raise EmailAlreadyTakenException(email.value)

        # raises WeakPasswordException
        self._password_policy.validate(command.password, email)

        user = self._users.create(email, command.password)
        return self._tokens.issue_for(user)
