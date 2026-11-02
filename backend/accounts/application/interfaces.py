from abc import ABC, abstractmethod
from dataclasses import dataclass

from accounts.domain.entities import User
from accounts.domain.value_objects import Email


@dataclass(frozen=True)
class TokenPair:
    access: str
    refresh: str


class UserRepository(ABC):
    @abstractmethod
    def exists_with_email(self, email: Email) -> bool:
        """Check whether a user with this email is already registered."""

    @abstractmethod
    def create(self, email: Email, password: str) -> User:
        """Persist a new user. Raises EmailAlreadyTaken if the email is in use."""

    @abstractmethod
    def get_by_credentials(self, email: Email, password: str) -> User | None:
        """Return the user if email and password match, otherwise None."""


class PasswordPolicy(ABC):
    @abstractmethod
    def validate(self, password: str, email: Email) -> None:
        """Raise WeakPassword if the password does not meet the requirements."""


class TokenService(ABC):
    @abstractmethod
    def issue_for(self, user: User) -> TokenPair:
        """Create a new access + refresh token pair for the user."""

    @abstractmethod
    def refresh(self, refresh_token: str) -> TokenPair:
        """Exchange a refresh token for a new pair. Raises InvalidToken."""
