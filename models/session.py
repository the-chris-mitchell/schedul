import base64
from datetime import datetime, time
from models.enums import DayBucket, TimeBucket
from models.film import Film
from models.venue import Venue


class Session:
    def __init__(self, film: Film, venue: Venue, start_time: datetime, link: str) -> None:
        self.film = film
        self.venue = venue
        self.link = link
        self.start_time = start_time
        self.booked = False
        self.end_time = self.get_end_time()
        self.day_bucket = self.get_day_bucket()
        self.time_bucket = self.get_time_bucket()
        self.start_time_formatted = datetime.fromisoformat(str(start_time)).strftime(f"%a {self.time_bucket.name.capitalize()} (%d/%m) %I:%M%p")
        self.end_time_formatted = datetime.fromisoformat(str(self.end_time)).strftime("%I:%M%p")
        self.sesion_id = self.generate_id()

    def generate_id(self) -> str:
        combined = (self.film.name + self.venue.name + datetime.fromisoformat(str(self.start_time)).strftime("%d/%m%I:%M%p")).replace(" ", "")
        return base64.b85encode(combined.encode()).decode()

    def book(self) -> None:
        self.booked = True

    def format(self) -> str:
        return f"{'✅' if self.booked else '👀'} {self.start_time_formatted}-{self.end_time_formatted}: {self.film.name} ({int(self.film.runtime.seconds/60)} minutes) @ {self.venue.name}"

    def get_end_time(self) -> datetime:
        return self.start_time + self.film.runtime

    def get_day_bucket(self) -> DayBucket:
        match datetime.fromisoformat(str(self.start_time)).date().weekday():
            case 5 | 6:
                return DayBucket.WEEKEND
            case 4:
                return DayBucket.FRIDAY
            case 1 | 2 | 3:
                return DayBucket.WEEKDAY
            case _:
                return DayBucket.NONE

    def get_time_bucket(self) -> TimeBucket:
        start_time = datetime.fromisoformat(str(self.start_time)).time()
        if start_time < time(13):
            return TimeBucket.MORNING
        elif start_time < time(17):
            return TimeBucket.AFTERNOON
        elif start_time > time(17):
            return TimeBucket.EVENING
        else:
            return TimeBucket.NONE