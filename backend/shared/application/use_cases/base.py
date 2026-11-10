from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True, slots=True)
class Command:
    pass


@dataclass(frozen=True, slots=True)
class ResponseDTO:
    pass


class UseCase(ABC):
    @abstractmethod
    def execute(self, command: Command) -> ResponseDTO: ...
