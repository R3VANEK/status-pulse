from dataclasses import dataclass

from accounts.application.interfaces import TokenPair, TokenService
from shared.application.use_cases.base import Command, UseCase


@dataclass(frozen=True, slots=True)
class RefreshTokensCommand(Command):
    refresh_token: str


class RefreshTokensUseCase(UseCase):
    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def execute(self, command: RefreshTokensCommand) -> TokenPair:
        return self._tokens.refresh(command.refresh_token)
