import datetime

from models.enums import DayBucket, TimeBucket
from pydantic import BaseModel


class TimePreference(BaseModel):
    day_bucket: DayBucket | None
    time_bucket: TimeBucket | None


class ScheduleRequest(BaseModel):
    excluded_dates: list[datetime.date] = []
    venues: list[str] = []
    time_preferences: list[TimePreference] = []
    max_daily_sessions: int = 1
    buffer_minutes: int = 30
    watchlist_only: bool = True
