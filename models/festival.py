from abc import ABC, abstractmethod
from models.session import Session


class Festival(ABC):
    @property
    @abstractmethod
    def full_name(self) -> str:
        pass

    @property
    @abstractmethod
    def short_name(self) -> str:
        pass

    @property
    @abstractmethod
    def sessions(self) -> list[Session]:
        pass
