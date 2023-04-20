from abc import ABC, abstractmethod
from datetime import timedelta

import httpx
from models.film import FilmBase, FilmCreate
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

    def create_resources_dev(self) -> None:
        self.scrape()
        for screening in self.film_screenings:
            film = create_film_if_required(
                name=screening.film_name,
                runtime=screening.film_runtime,
                year=screening.film_year,
            )
            venue = create_venue_if_required(name=screening.venue_name)
            festival = create_festival_if_required(
                full_name=self.full_name, short_name=self.short_name
            )
            create_screening_if_required(
                start_time=screening.screening_start_time,
                end_time=screening.screening_start_time
                + timedelta(minutes=film.runtime),
                link=screening.screening_link,
                film_id=film.id,  # type: ignore
                venue_id=venue.id,  # type: ignore
                festival_id=festival.id,  # type: ignore
            )
        print(f"Loaded {len(self.film_screenings)} screening(s) into DB")

    def create_resources_prod(self) -> None:
        self.scrape()
        for screening in self.film_screenings:
            check_film = httpx.get(
                f"https://schedul-production.up.railway.app/films?film_name={screening.film_name}"
            ).json()
            if len(check_film) == 0:
                film_payload = {
                    "name": screening.film_name,
                    "runtime": screening.film_runtime,
                    "year": screening.film_year,
                }
                film_response = httpx.post(
                    "https://schedul-production.up.railway.app/films", json=film_payload
                ).json()
            else:
                film_response = check_film[0]
            venue_response = httpx.post(
                "https://schedul-production.up.railway.app/venues",
                json={"name": screening.venue_name},
            ).json()
            festival_payload = {
                "full_name": self.full_name,
                "short_name": self.short_name,
            }
            festival_response = httpx.post(
                "https://schedul-production.up.railway.app/festivals",
                json=festival_payload,
            ).json()
            screening_payload = {
                "start_time": screening.screening_start_time.isoformat(),
                "end_time": (
                    screening.screening_start_time
                    + timedelta(minutes=screening.film_runtime)
                ).isoformat(),
                "link": screening.screening_link,
                "film_id": film_response["id"],
                "venue_id": venue_response["id"],
                "festival_id": festival_response["id"],
            }
            httpx.post(
                "https://schedul-production.up.railway.app/screenings",
                json=screening_payload,
            )
