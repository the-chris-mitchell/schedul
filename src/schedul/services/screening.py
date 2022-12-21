from datetime import datetime, time

from clients.sql import engine
from models.enums import DayBucket, TimeBucket
from models.screening import Screening
from sqlmodel import Session, select


def create_screening(
    start_time: datetime,
    end_time: datetime,
    link: str,
    film_id: int,
    venue_id: int,
    festival_id: int,
) -> Screening:
    with Session(engine) as session:
        db_screening = Screening(
            start_time=start_time,
            end_time=end_time,
            link=link,
            film_id=film_id,
            venue_id=venue_id,
            festival_id=festival_id,
        )
        session.add(db_screening)
        session.commit()
        session.refresh(db_screening)
        return db_screening


def create_screening_if_required(
    start_time: datetime,
    end_time: datetime,
    link: str,
    film_id: int,
    venue_id: int,
    festival_id: int,
) -> Screening:
    with Session(engine) as session:
        query = session.exec(
            select(Screening)
            .where(Screening.film_id == film_id)
            .where(Screening.festival_id == festival_id)
            .where(Screening.start_time == start_time)
        ).first()
        return query or create_screening(
            start_time=start_time,
            end_time=end_time,
            link=link,
            film_id=film_id,
            venue_id=venue_id,
            festival_id=festival_id,
        )


def get_day_bucket(start_time: datetime) -> DayBucket:
    match start_time.date().weekday():
        case 5 | 6:
            return DayBucket.WEEKEND
        case 4:
            return DayBucket.FRIDAY
        case 0 | 1 | 2 | 3:
            return DayBucket.WEEKDAY
        case _:
            return DayBucket.NONE


def get_time_bucket(start_time: datetime) -> TimeBucket:
    start_time_time = start_time.time()
    if start_time_time < time(13):
        return TimeBucket.MORNING
    elif start_time_time < time(18):
        return TimeBucket.AFTERNOON
    elif start_time_time >= time(18):
        return TimeBucket.EVENING
    else:
        return TimeBucket.NONE

    # @property
    # def start_time_formatted(self) -> str:
    #     return datetime.fromisoformat(str(self.start_time)).strftime(f"%a {self.time_bucket.name.capitalize()} (%d/%m) %I:%M%p")

    # @property
    # def end_time_formatted(self) -> str:
    #     return datetime.fromisoformat(str(self.end_time)).strftime("%I:%M%p")

    # @property
    # def id(self) -> str:
    #     short_name = ''.join([x[0] for x in self.film.name.split(' ')])
    #     short_venue = ''.join([x[0] for x in self.venue.normalised_name.split(' ')])
    #     combined = (short_name + short_venue + datetime.fromisoformat(str(self.start_time)).strftime("%d/%m%I:%M%p")).replace(" ", "")
    #     return base64.b64encode(combined.encode()).decode()

    # @property
    # def formatted(self) -> str:
    #     return f"{'✅' if self.booked else '👀'} {self.start_time_formatted}-{self.end_time_formatted}: {self.film.name} ({self.film.runtime} minutes) @ {self.venue.normalised_name}"

    # def book(self) -> None:
    #     self.booked = True
