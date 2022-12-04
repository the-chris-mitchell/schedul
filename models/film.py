from datetime import timedelta

from utils.config import CONFIG


class Film:
    def __init__(self, name: str, runtime: timedelta, year: int = None) -> None:
        self.name = name
        self.runtime = runtime
        self.year = year
        self.watchlist = self.name in CONFIG.watchlist