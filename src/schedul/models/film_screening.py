from dataclasses import dataclass
from datetime import datetime

from models.film import FilmBase
from models.venue import VenueBase


@dataclass
class FilmScreening:
    film: FilmBase
    venue: VenueBase
    screening_start_time_utc: datetime
    screening_link: str
