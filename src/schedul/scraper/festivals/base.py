from abc import ABC, abstractmethod
from datetime import timedelta
from models.film_screening import FilmScreening

from services.festival import create_festival_if_required
from services.film import create_film_if_required
from services.screening import create_screening_if_required
from services.venue import create_venue_if_required


class Festival(ABC):
    def __init__(self) -> None:
        self.film_screenings: list[FilmScreening] = []

    @property
    @abstractmethod
    def full_name(self) -> str:
        pass

    @property
    @abstractmethod
    def short_name(self) -> str:
        pass

    @abstractmethod
    def scrape(self) -> None:
        pass

    def create_resources(self) -> None:
        self.scrape()
        for screening in self.film_screenings:
            film = create_film_if_required(
                name=screening.film_name,
                runtime=screening.film_runtime,
                year=screening.film_year
            )
            venue = create_venue_if_required(
                name=screening.venue_name
            )
            festival = create_festival_if_required(
                full_name=self.full_name,
                short_name=self.short_name
            )
            create_screening_if_required(
                start_time=screening.screening_start_time,
                end_time=screening.screening_start_time + timedelta(minutes=film.runtime),
                link=screening.screening_link,
                film_id=film.id, # type: ignore
                venue_id=venue.id, # type: ignore
                festival_id=festival.id # type: ignore
            )
        print(f"Loaded {len(self.film_screenings)} screening(s) into DB")