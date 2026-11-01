from django.test import SimpleTestCase

from accounts.application.interfaces import (
    PasswordPolicy,
    TokenPair,
    TokenService,
    UserRepository,
)
from accounts.application.use_cases.register_user import (
    RegisterUser,
    RegisterUserCommand,
)
from accounts.domain.entities import User
from accounts.domain.exceptions import EmailAlreadyTaken, InvalidEmail, WeakPassword
from accounts.domain.value_objects import Email


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.passwords: dict[str, str] = {}

    def exists_with_email(self, email: Email) -> bool:
        return email.value in self.passwords

    def create(self, email: Email, password: str) -> User:
        self.passwords[email.value] = password
        return User(id=len(self.passwords), email=email)

    def get_by_credentials(self, email: Email, password: str) -> User | None:
        raise NotImplementedError


class MinLengthPasswordPolicy(PasswordPolicy):
    def validate(self, password: str, email: Email) -> None:
        if len(password) < 8:
            raise WeakPassword(["Too short."])


class FakeTokenService(TokenService):
    def issue_for(self, user: User) -> TokenPair:
        return TokenPair(access=f"access-{user.id}", refresh=f"refresh-{user.id}")

    def refresh(self, refresh_token: str) -> TokenPair:
        raise NotImplementedError


class RegisterUserTests(SimpleTestCase):
    def setUp(self) -> None:
        self.users = InMemoryUserRepository()
        self.use_case = RegisterUser(
            users=self.users,
            password_policy=MinLengthPasswordPolicy(),
            tokens=FakeTokenService(),
        )

    def test_creates_user_and_returns_tokens(self) -> None:
        tokens = self.use_case.execute(
            RegisterUserCommand(email="Jan@Example.com", password="s3cret-pass")
        )

        self.assertEqual(tokens, TokenPair(access="access-1", refresh="refresh-1"))
        self.assertIn("jan@example.com", self.users.passwords)

    def test_rejects_taken_email(self) -> None:
        command = RegisterUserCommand(email="jan@example.com", password="s3cret-pass")
        self.use_case.execute(command)

        with self.assertRaises(EmailAlreadyTaken):
            self.use_case.execute(command)

    def test_rejects_invalid_email(self) -> None:
        with self.assertRaises(InvalidEmail):
            self.use_case.execute(
                RegisterUserCommand(email="not-an-email", password="s3cret-pass")
            )

    def test_rejects_weak_password_and_does_not_create_user(self) -> None:
        with self.assertRaises(WeakPassword):
            self.use_case.execute(
                RegisterUserCommand(email="jan@example.com", password="short")
            )

        self.assertEqual(self.users.passwords, {})
