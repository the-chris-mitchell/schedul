from datetime import datetime, timezone

from schedul.models.film import FilmBase
from schedul.models.screening import FilmScreening
from schedul.models.venue import VenueBase
from schedul.scraper.festivals.base import Festival


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
