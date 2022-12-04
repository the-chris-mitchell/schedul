from dataclasses import dataclass
from datetime import datetime


@dataclass
class FilmScreening:
    film_name: str
    film_runtime: int
    film_year: int
    venue_name: str
    screening_start_time: datetime
    screening_link: str
