from datetime import date
from models.enums import DayBucket, TimeBucket
from models.venue import Venue


class Preference:
    def __init__(self, time_bucket: str=None, day_bucket: str=None, venue: str = None) -> None:
        self.day_bucket = DayBucket[day_bucket.upper()] if day_bucket else None
        self.time_bucket = TimeBucket[time_bucket.upper()] if time_bucket else None
        self.venue = Venue(venue) if venue else None
        self.date = None # to implement