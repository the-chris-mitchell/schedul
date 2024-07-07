import urllib.parse
from abc import ABC, abstractmethod
from datetime import timedelta

import httpx
from sqlmodel import Session

from clients.sql import engine
from models.festival import FestivalCreate, FestivalPublic
from models.film import FilmCreate, FilmPublic
from models.screening import FilmScreening, ScreeningCreate
from models.venue import VenueCreate, VenuePublic
from services.festival import create_festival_if_required_db
from services.film import create_film_if_required_db
from services.screening import create_screening_if_required_db
from services.venue import create_venue_if_required

SCHEDUL_URL_PROD = "https://schedul-production.up.railway.app"


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

        with Session(engine) as session:
            festival = FestivalPublic.model_validate(
                create_festival_if_required_db(
                    session=session,
                    festival=FestivalCreate(
                        full_name=self.full_name, short_name=self.short_name
                    ),
                )
            )

            for screening in self.film_screenings:
                print(
                    f"{screening.film.name} @ {screening.venue.name} ({screening.screening_start_time_utc.strftime('%A %d %B %I:%M%p')} UTC)",
                    end=" ",
                )

                film = FilmPublic.model_validate(
                    create_film_if_required_db(
                        session=session,
                        film=FilmCreate(
                            name=screening.film.name, runtime=screening.film.runtime
                        ),
                    )
                )
                venue = VenuePublic.model_validate(
                    create_venue_if_required(
                        session=session, venue=VenueCreate(name=screening.venue.name)
                    )
                )

                screening = ScreeningCreate(
                    start_time_utc=screening.screening_start_time_utc,
                    end_time_utc=screening.screening_start_time_utc
                    + timedelta(minutes=film.runtime),
                    link=screening.screening_link,
                    strand=screening.strand,
                    film_id=film.id,
                    venue_id=venue.id,
                    festival_id=festival.id,
                )
                create_screening_if_required_db(session=session, screening=screening)

                print("✅")

    def create_resources_prod(self) -> None:
        self.scrape()

        film_ids = {}
        for film in {screening.film for screening in self.film_screenings}:
            print(f"🎬 {film.name}", end=" ")
            check_film = httpx.get(
                f"{SCHEDUL_URL_PROD}/films?film_name={urllib.parse.quote(film.name)}"
            )
            if check_film.status_code == 204:
                film_response = httpx.post(
                    "{SCHEDUL_URL_PROD}/films", json=film.dict()
                ).json()
            else:
                film_response = check_film.json()[0]
            film_ids[film.name] = film_response["id"]
            # TODO: error handling
            print("✅")

        venue_ids = {}
        for venue in {screening.venue for screening in self.film_screenings}:
            print(f"🏠 {venue.name}", end=" ")
            check_venue = httpx.get(
                f"{SCHEDUL_URL_PROD}/venues?venue_name={urllib.parse.quote(venue.name)}"
            )
            if check_venue.status_code == 204:
                venue_response = httpx.post(
                    "{SCHEDUL_URL_PROD}/venues",
                    json=venue.dict(),
                ).json()
            else:
                venue_response = check_venue.json()[0]
            venue_ids[venue.name] = venue_response["id"]
            # TODO: proper error handling
            print("✅")

        print(f"🎊 {self.full_name}", end=" ")
        check_festival = httpx.get(
            f"{SCHEDUL_URL_PROD}/festivals?short_name={urllib.parse.quote(self.short_name)}"
        )
        if check_festival.status_code == 204:
            festival_response = httpx.post(
                "{SCHEDUL_URL_PROD}/festivals",
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
                "{SCHEDUL_URL_PROD}/screenings",
                json=screening_payload,
            )
            if screening_response.is_success:
                print("✅")
            else:
                print("❌")
