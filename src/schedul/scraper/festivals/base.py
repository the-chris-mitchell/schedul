import urllib.parse
from abc import ABC, abstractmethod
from datetime import timedelta

import httpx

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
            print(
                f"{screening.film.name} @ {screening.venue.name} ({screening.screening_start_time_utc.strftime('%A %d %B %I:%M%p')} UTC)",
                end=" ",
            )
            film = create_film_if_required(
                name=screening.film.name, runtime=screening.film.runtime
            )
            venue = create_venue_if_required(name=screening.venue.name)
            festival = create_festival_if_required(
                full_name=self.full_name, short_name=self.short_name
            )
            create_screening_if_required(
                start_time_utc=screening.screening_start_time_utc,
                end_time_utc=screening.screening_start_time_utc
                + timedelta(minutes=film.runtime),
                link=screening.screening_link,
                film_id=film.id,  # type: ignore
                venue_id=venue.id,  # type: ignore
                festival_id=festival.id,  # type: ignore
            )
            print("✅")

    def create_resources_prod(self) -> None:
        self.scrape()

        film_ids = {}
        for film in {screening.film for screening in self.film_screenings}:
            print(f"🎬 {film.name}", end=" ")
            check_film = httpx.get(
                f"https://schedul-production.up.railway.app/films?film_name={urllib.parse.quote(film.name)}"
            )
            if check_film.status_code == 204:
                film_response = httpx.post(
                    "https://schedul-production.up.railway.app/films", json=film.dict()
                ).json()
            else:
                film_response = check_film.json()[0]
            film_ids[film.name] = film_response["id"]
            # TODO: proper error handling
            print("✅")

        venue_ids = {}
        for venue in {screening.venue for screening in self.film_screenings}:
            print(f"🏠 {venue.name}", end=" ")
            check_venue = httpx.get(
                f"https://schedul-production.up.railway.app/venues?venue_name={urllib.parse.quote(venue.name)}"
            )
            if check_venue.status_code == 204:
                venue_response = httpx.post(
                    "https://schedul-production.up.railway.app/venues",
                    json=venue.dict(),
                ).json()
            else:
                venue_response = check_venue.json()[0]
            venue_ids[venue.name] = venue_response["id"]
            # TODO: proper error handling
            print("✅")

        print(f"🎊 {self.full_name}", end=" ")
        check_festival = httpx.get(
            f"https://schedul-production.up.railway.app/festivals?short_name={urllib.parse.quote(self.short_name)}"
        )
        if check_festival.status_code == 204:
            festival_response = httpx.post(
                "https://schedul-production.up.railway.app/festivals",
                json={"full_name": self.full_name, "short_name": self.short_name},
            ).json()
        else:
            festival_response = check_festival.json()[0]
        festival_id = festival_response["id"]
        # TODO: proper error handling
        print("✅")

        for screening in self.film_screenings:
            print(
                f"🎥 {screening.film.name} @ {screening.venue.name} ({screening.screening_start_time_utc.strftime('%A %d %B %I:%M%p')} UTC)",
                end=" ",
            )
            screening_payload = {
                "start_time_utc": screening.screening_start_time_utc.isoformat(),
                "end_time_utc": (
                    screening.screening_start_time_utc
                    + timedelta(minutes=screening.film.runtime)
                ).isoformat(),
                "link": screening.screening_link,
                "film_id": film_ids[screening.film.name],
                "venue_id": venue_ids[screening.venue.name],
                "festival_id": festival_id,
            }
            screening_response = httpx.post(
                "https://schedul-production.up.railway.app/screenings",
                json=screening_payload,
            )
            if screening_response.is_success:
                print("✅")
            else:
                print("❌")
