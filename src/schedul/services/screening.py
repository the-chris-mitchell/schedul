from datetime import datetime, time

import arrow
from sqlmodel import Session, select

from clients.sql import engine
from models.enums import DayBucket, TimeBucket
from models.screening import Screening


def create_screening(
    start_time_utc: datetime,
    end_time_utc: datetime,
    link: str,
    film_id: int,
    venue_id: int,
    festival_id: int,
) -> Screening:
    with Session(engine) as session:
        db_screening = Screening(
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
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
    start_time_utc: datetime,
    end_time_utc: datetime,
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
            .where(Screening.start_time_utc == start_time_utc)
        ).first()
        return query or create_screening(
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
            link=link,
            film_id=film_id,
            venue_id=venue_id,
            festival_id=festival_id,
        )


def get_day_bucket(start_time: datetime, time_zone: str) -> DayBucket:
    match arrow.get(start_time).to(time_zone).date().weekday():
        case 5 | 6:
            return DayBucket.WEEKEND
        case 4:
            return DayBucket.FRIDAY
        case 0 | 1 | 2 | 3:
            return DayBucket.WEEKDAY
        case _:
            return DayBucket.NONE


def get_time_bucket(start_time: datetime, time_zone: str) -> TimeBucket:
    start_time_time = arrow.get(start_time).to(time_zone).time()
    if start_time_time < time(13):
        return TimeBucket.MORNING
    elif start_time_time < time(18):
        return TimeBucket.AFTERNOON
    elif start_time_time >= time(18):
        return TimeBucket.EVENING
    else:
        return TimeBucket.NONE
