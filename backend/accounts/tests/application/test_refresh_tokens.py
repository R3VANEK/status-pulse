from django.test import SimpleTestCase

from accounts.application.use_cases.refresh_tokens import (
    RefreshTokens,
    RefreshTokensCommand,
)
from accounts.domain.entities import User
from accounts.domain.exceptions import InvalidToken
from accounts.domain.value_objects import Email
from accounts.tests.application.fakes import FakeTokenService


class RefreshTokensTests(SimpleTestCase):
    def setUp(self) -> None:
        self.tokens = FakeTokenService()
        self.initial = self.tokens.issue_for(User(id=1, email=Email("jan@example.com")))
        self.use_case = RefreshTokens(tokens=self.tokens)

    def test_returns_new_token_pair(self) -> None:
        refreshed = self.use_case.execute(RefreshTokensCommand(self.initial.refresh))

        self.assertNotEqual(refreshed.access, self.initial.access)
        self.assertNotEqual(refreshed.refresh, self.initial.refresh)

    def test_used_refresh_token_cannot_be_reused(self) -> None:
        self.use_case.execute(RefreshTokensCommand(self.initial.refresh))

        with self.assertRaises(InvalidToken):
            self.use_case.execute(RefreshTokensCommand(self.initial.refresh))

    def test_rejects_unknown_token(self) -> None:
        with self.assertRaises(InvalidToken):
            self.use_case.execute(RefreshTokensCommand("garbage"))
