import base64
from datetime import datetime, time, timedelta

from sqlmodel import SQLModel

from models.enums import DayBucket, TimeBucket
from models.film import Film
from models.venue import Venue


class SessionSQL(SQLModel):
    film: Film
    venue: Venue
    start_time: datetime
    link: str
    booked: bool = False

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.film.runtime)

    @property
    def day_bucket(self) -> DayBucket:
        match datetime.fromisoformat(str(self.start_time)).date().weekday():
            case 5 | 6:
                return DayBucket.WEEKEND
            case 4:
                return DayBucket.FRIDAY
            case 0 | 1 | 2 | 3:
                return DayBucket.WEEKDAY
            case _:
                return DayBucket.NONE
    
    @property
    def time_bucket(self) -> TimeBucket:
        start_time = datetime.fromisoformat(str(self.start_time)).time()
        if start_time < time(13):
            return TimeBucket.MORNING
        elif start_time < time(17):
            return TimeBucket.AFTERNOON
        elif start_time > time(17):
            return TimeBucket.EVENING
        else:
            return TimeBucket.NONE

    @property
    def start_time_formatted(self) -> str:
        return datetime.fromisoformat(str(self.start_time)).strftime(f"%a {self.time_bucket.name.capitalize()} (%d/%m) %I:%M%p")

    @property
    def end_time_formatted(self) -> str:
        return datetime.fromisoformat(str(self.end_time)).strftime("%I:%M%p")

    @property
    def id(self) -> str:
        short_name = ''.join([x[0] for x in self.film.name.split(' ')])
        short_venue = ''.join([x[0] for x in self.venue.normalised_name.split(' ')])
        combined = (short_name + short_venue + datetime.fromisoformat(str(self.start_time)).strftime("%d/%m%I:%M%p")).replace(" ", "")
        return base64.b64encode(combined.encode()).decode()

    @property
    def formatted(self) -> str:
        return f"{'✅' if self.booked else '👀'} {self.start_time_formatted}-{self.end_time_formatted}: {self.film.name} ({self.film.runtime} minutes) @ {self.venue.normalised_name}"

    def book(self) -> None:
        self.booked = True
