from models.enums import DayBucket, TimeBucket
from pydantic import BaseModel


class Preference(BaseModel):
    venue_name: str | None
    day_bucket: DayBucket | None
    time_bucket: TimeBucket | None
