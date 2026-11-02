from dataclasses import dataclass

from accounts.application.interfaces import (
    PasswordPolicy,
    TokenPair,
    TokenService,
    UserRepository,
)
from accounts.domain.exceptions import EmailAlreadyTaken
from accounts.domain.value_objects import Email


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str


class RegisterUser:
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
        email = Email(command.email)  # raises InvalidEmail

        if self._users.exists_with_email(email):
            raise EmailAlreadyTaken(email.value)

        self._password_policy.validate(command.password, email)  # raises WeakPassword

        user = self._users.create(email, command.password)
        return self._tokens.issue_for(user)
