from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

import arrow
from sqlmodel import Field, Relationship, SQLModel

from models.enums import DayBucket, TimeBucket
from models.festival import Festival
from models.film import Film
from models.venue import Venue


class ScreeningBase(SQLModel):
    start_time_utc: datetime
    end_time_utc: datetime
    link: str
    film_id: int = Field(foreign_key="film.id")
    venue_id: int = Field(foreign_key="venue.id")
    festival_id: int = Field(foreign_key="festival.id")

    def get_day_bucket(self, time_zone: str) -> DayBucket:
        match arrow.get(self.start_time_utc).to(time_zone).date().weekday():
            case 5 | 6:
                return DayBucket.WEEKEND
            case 0 | 1 | 2 | 3 | 4:
                return DayBucket.WEEKDAY
            case _:
                return DayBucket.NONE

    def get_time_bucket(self, time_zone: str) -> TimeBucket:
        start_time_time = arrow.get(self.start_time_utc).to(time_zone).time()
        if start_time_time < time(12):
            return TimeBucket.MORNING
        elif start_time_time < time(15):
            return TimeBucket.EARLY_AFTERNOON
        elif start_time_time < time(18):
            return TimeBucket.LATE_AFTERNOON
        elif start_time_time < time(21):
            return TimeBucket.EVENING
        elif start_time_time >= time(21):
            return TimeBucket.LATE
        else:
            return TimeBucket.NONE


class Screening(ScreeningBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film: Film = Relationship()
    venue: Venue = Relationship()
    festival: Festival = Relationship()

    def format(self, time_zone: str):
        elements: list[str] = []
        elements.append(self.film.name)
        elements.append(self.venue.name)
        elements.append(arrow.get(self.start_time_utc).to(time_zone).format("h:mm a"))
        elements.append(self.get_time_bucket(time_zone=time_zone).name)
        return " | ".join(elements)


class ScreeningCreate(ScreeningBase):
    pass


class ScreeningRead(ScreeningBase):
    id: int
    film: Film
    venue: Venue


@dataclass
class ScoredScreening:
    day_bucket: DayBucket
    time_bucket: TimeBucket
    screening: ScreeningRead
    score: int = 0
    booked: bool = False
    in_watchlist: bool = False

    def format(self, time_zone: str):
        screening = Screening.model_validate(self.screening)
        elements: list[str] = []
        if self.in_watchlist:
            elements.append("👀")
        elements.append(screening.format(time_zone=time_zone))
        elements.append(f"Score: {self.score}")
        return " | ".join(elements)
