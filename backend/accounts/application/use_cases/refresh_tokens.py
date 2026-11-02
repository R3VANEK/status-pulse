from dataclasses import dataclass

from accounts.application.interfaces import TokenPair, TokenService


@dataclass(frozen=True)
class RefreshTokensCommand:
    refresh_token: str


class RefreshTokens:
    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def execute(self, command: RefreshTokensCommand) -> TokenPair:
        return self._tokens.refresh(command.refresh_token)  # raises InvalidToken
