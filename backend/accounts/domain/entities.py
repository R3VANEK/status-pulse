from dataclasses import dataclass

from accounts.domain.value_objects import Email


@dataclass
class User:
    email: Email
    id: int | None
    username: str
    first_name: str
    surname: str
    phone_number: str
    is_active: bool = True
