from datetime import date
from enums import DayBucket, TimeBucket
from models.venue import Venue


class Preference:
    def __init__(self, time_bucket: TimeBucket=None, day_bucket: DayBucket=None, date: date=None, venue: Venue = None) -> None:
        self.day_bucket = day_bucket
        self.time_bucket = time_bucket
        self.date = date
        self.venue = venue