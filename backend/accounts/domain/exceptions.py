from shared.domain.exceptions import DomainException


class AccountsException(DomainException):
    """Base class for all business errors of the accounts domain."""


class InvalidEmailException(AccountsException):
    def __init__(self, email: str) -> None:
        super().__init__(f"'{email}' is not a valid email address.")
        self.email = email


class EmailAlreadyTakenException(AccountsException):
    def __init__(self, email: str) -> None:
        super().__init__(f"A user with email '{email}' already exists.")
        self.email = email


class WeakPasswordException(AccountsException):
    def __init__(self, reasons: list[str]) -> None:
        super().__init__(" ".join(reasons))
        self.reasons = reasons


class InvalidCredentialsException(AccountsException):
    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class InvalidTokenException(AccountsException):
    def __init__(self) -> None:
        super().__init__("Token is invalid or expired.")
