from dataclasses import dataclass

from accounts.application.interfaces import TokenPair, TokenService
from shared.application.use_cases.base import (
    Command as BaseCommand,
    UseCase as BaseUseCase,
)


@dataclass(frozen=True, slots=True)
class Command(BaseCommand):
    refresh_token: str


class UseCase(BaseUseCase):
    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def execute(self, command: Command) -> TokenPair:
        return self._tokens.refresh(command.refresh_token)
