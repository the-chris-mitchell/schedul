import datetime
import uuid as uuid_pkg

from pydantic import BaseModel

from models.enums import DayBucket, TimeBucket


class Preference(BaseModel):
    score: int


class TimePreference(Preference):
    day_bucket: DayBucket
    time_bucket: TimeBucket


class VenuePreference(Preference):
    venue_name: str


class ScheduleRequest(BaseModel):
    excluded_dates: list[datetime.date] = []
    venue_preferences: list[VenuePreference] = []
    time_preferences: list[TimePreference] = []
    max_daily_sessions: int = 1
    buffer_minutes: int = 30
    watchlist_only: bool = True
    future_only: bool = True
    time_zone: str
    user_uuid: uuid_pkg.UUID
