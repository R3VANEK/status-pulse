from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any


@dataclass(frozen=True, slots=True)
class Command:
    pass


@dataclass(frozen=True, slots=True)
class ResponseDTO:
    pass


class UseCase(ABC):
    @abstractmethod
    def execute(self, command: Any) -> Any: ...
