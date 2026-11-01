from django.test import SimpleTestCase

from accounts.application.interfaces import TokenPair
from accounts.application.use_cases.register_user import (
    RegisterUser,
    RegisterUserCommand,
)
from accounts.domain.exceptions import EmailAlreadyTaken, InvalidEmail, WeakPassword
from accounts.tests.application.fakes import (
    FakeTokenService,
    InMemoryUserRepository,
    MinLengthPasswordPolicy,
)


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
