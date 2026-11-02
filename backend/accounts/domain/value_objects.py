import re
from dataclasses import dataclass

from accounts.domain.exceptions import InvalidEmail

# Simple sanity check: something@something.something, no spaces.
# Full RFC validation is not the goal here.
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise InvalidEmail(self.value)
        # frozen dataclass blocks normal assignment, so we bypass it once, during creation
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
