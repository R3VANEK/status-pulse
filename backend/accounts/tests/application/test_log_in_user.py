from django.test import SimpleTestCase

from accounts.application.interfaces import TokenPair
from accounts.application.use_cases.log_in_user import LogInUser, LogInUserCommand
from accounts.domain.exceptions import InvalidCredentials
from accounts.domain.value_objects import Email
from accounts.tests.application.fakes import FakeTokenService, InMemoryUserRepository


class LogInUserTests(SimpleTestCase):
    def setUp(self) -> None:
        self.users = InMemoryUserRepository()
        self.users.create(Email("jan@example.com"), "s3cret-pass")
        self.use_case = LogInUser(users=self.users, tokens=FakeTokenService())

    def test_returns_tokens_for_valid_credentials(self) -> None:
        tokens = self.use_case.execute(
            LogInUserCommand(email="jan@example.com", password="s3cret-pass")
        )

        self.assertEqual(tokens, TokenPair(access="access-1", refresh="refresh-1"))

    def test_email_is_case_insensitive(self) -> None:
        tokens = self.use_case.execute(
            LogInUserCommand(email="JAN@Example.com", password="s3cret-pass")
        )

        self.assertEqual(tokens.access, "access-1")

    def test_rejects_wrong_password(self) -> None:
        with self.assertRaises(InvalidCredentials):
            self.use_case.execute(
                LogInUserCommand(email="jan@example.com", password="wrong-pass")
            )

    def test_rejects_unknown_email(self) -> None:
        with self.assertRaises(InvalidCredentials):
            self.use_case.execute(
                LogInUserCommand(email="nobody@example.com", password="s3cret-pass")
            )

    def test_rejects_malformed_email_without_revealing_it(self) -> None:
        with self.assertRaises(InvalidCredentials):
            self.use_case.execute(
                LogInUserCommand(email="not-an-email", password="s3cret-pass")
            )

    def test_rejects_inactive_user(self) -> None:
        self.users.users["jan@example.com"].is_active = False

        with self.assertRaises(InvalidCredentials):
            self.use_case.execute(
                LogInUserCommand(email="jan@example.com", password="s3cret-pass")
            )
