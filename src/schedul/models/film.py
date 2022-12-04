from models.base import Base

from utils.config import CONFIG

class Film(Base):
    name: str
    runtime: int
    year: int

    @property
    def watchlist(self) -> bool:
        return self.name in CONFIG.watchlist

    def __hash__(self):
        return hash((self.name))