import datetime
import uuid as uuid_pkg

from pydantic import BaseModel

from models.enums import DayBucket, TimeBucket


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
    booked_session_ids: list[int] = []
    time_zone: str
    user_uuid: uuid_pkg.UUID
