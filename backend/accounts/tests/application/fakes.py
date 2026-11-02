"""In-memory implementations of application interfaces, used by unit tests."""

from accounts.application.interfaces import (
    PasswordPolicy,
    TokenPair,
    TokenService,
    UserRepository,
)
from accounts.domain.entities import User
from accounts.domain.exceptions import InvalidToken, WeakPassword
from accounts.domain.value_objects import Email


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.passwords: dict[str, str] = {}

    def exists_with_email(self, email: Email) -> bool:
        return email.value in self.users

    def create(self, email: Email, password: str) -> User:
        user = User(id=len(self.users) + 1, email=email)
        self.users[email.value] = user
        self.passwords[email.value] = password
        return user

    def get_by_credentials(self, email: Email, password: str) -> User | None:
        if self.passwords.get(email.value) != password:
            return None
        return self.users[email.value]


class MinLengthPasswordPolicy(PasswordPolicy):
    def validate(self, password: str, email: Email) -> None:
        if len(password) < 8:
            raise WeakPassword(["Too short."])


class FakeTokenService(TokenService):
    """Issues predictable tokens: access-1/refresh-1, access-2/refresh-2, ..."""

    def __init__(self) -> None:
        self._issued = 0
        self.valid_refresh_tokens: set[str] = set()

    def issue_for(self, user: User) -> TokenPair:
        return self._issue_pair()

    def refresh(self, refresh_token: str) -> TokenPair:
        if refresh_token not in self.valid_refresh_tokens:
            raise InvalidToken()
        # rotation: the used refresh token stops being valid
        self.valid_refresh_tokens.remove(refresh_token)
        return self._issue_pair()

    def _issue_pair(self) -> TokenPair:
        self._issued += 1
        pair = TokenPair(
            access=f"access-{self._issued}", refresh=f"refresh-{self._issued}"
        )
        self.valid_refresh_tokens.add(pair.refresh)
        return pair
