from dataclasses import dataclass

from accounts.domain.value_objects import Email


@dataclass
class User:
    email: Email
    id: int | None = None
    first_name: str = ""
    surname: str = ""
    is_active: bool = True
