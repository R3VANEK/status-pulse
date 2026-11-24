from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class File:
    name: str
    content: bytes
    content_type: str
    content_size: int
