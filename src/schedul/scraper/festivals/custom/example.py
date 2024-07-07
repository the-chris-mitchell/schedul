from datetime import datetime, timezone

from models.film import FilmBase
from models.screening import FilmScreening
from models.venue import VenueBase
from scraper.festivals.base import Festival


class TestFest(Festival):
    @property
    def full_name(self):
        return "Test Fest"

    @property
    def short_name(self):
        return "tf"

    def scrape(self):
        screening = FilmScreening(
            film=FilmBase(name="Citizen Kane", runtime=119),
            venue=VenueBase(name="Embassy Grand"),
            screening_start_time_utc=datetime.now(timezone.utc),
            screening_link="https://example.com",
        )
        self.film_screenings.append(screening)
