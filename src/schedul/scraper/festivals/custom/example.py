from datetime import datetime, timezone
from models.film_screening import FilmScreening
from scraper.festivals.base import Festival


class TestFest(Festival):
    @property
    def full_name(self):
        return "Test Fest"

    @property
    def short_name(self):
        return "tf"

    def scrape(self):
        film1 = FilmScreening(
            film_name="Citizen Kane",
            film_runtime=119,
            film_year=1941,
            venue_name="Embassy Grand",
            screening_start_time=datetime.now(timezone.utc),
            screening_link="https://example.com",
        )
        self.film_screenings.append(film1)
