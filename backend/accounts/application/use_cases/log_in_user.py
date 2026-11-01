from dataclasses import dataclass

from accounts.application.interfaces import TokenPair, TokenService, UserRepository
from accounts.domain.exceptions import InvalidCredentials, InvalidEmail
from accounts.domain.value_objects import Email


@dataclass(frozen=True)
class LogInUserCommand:
    email: str
    password: str


class LogInUser:
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    def execute(self, command: LogInUserCommand) -> TokenPair:
        try:
            email = Email(command.email)
        except InvalidEmail:
            # Do not reveal which part was wrong.
            raise InvalidCredentials() from None

        user = self._users.get_by_credentials(email, command.password)
        if user is None or not user.is_active:
            raise InvalidCredentials()

        return self._tokens.issue_for(user)
