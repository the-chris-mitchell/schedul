from dataclasses import dataclass
from typing import List

from models.film import Film


@dataclass
class WatchlistFilm:
    film: Film
    in_watchlist: bool


@dataclass
class Watchlist:
    films: List[WatchlistFilm]
