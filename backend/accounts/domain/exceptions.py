class AccountsError(Exception):
    """Base class for all business errors of the accounts domain."""


class InvalidEmail(AccountsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"'{email}' is not a valid email address.")
        self.email = email


class EmailAlreadyTaken(AccountsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists.")
        self.email = email


class WeakPassword(AccountsError):
    def __init__(self, reasons: list[str]) -> None:
        super().__init__(" ".join(reasons))
        self.reasons = reasons


class InvalidCredentials(AccountsError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class InvalidToken(AccountsError):
    def __init__(self) -> None:
        super().__init__("Token is invalid or expired.")
