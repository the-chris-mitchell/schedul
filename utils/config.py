from datetime import date
from strictyaml import (Datetime, EmptyList, EmptyNone, Enum,  # type: ignore
                        Int, Map, Optional, Seq, Str, load)

from models.enums import DayBucket, TimeBucket


preferences_schema = Seq(Map({
        Optional("venue"): Str(),
        Optional("time-bucket"): Enum([e.name.lower() for e in TimeBucket]),
        Optional("day-bucket"): Enum([e.name.lower() for e in DayBucket])
    }))

schema = Map({
    "max-sessions": Int(),
    "iterations": Int(),
    "preferences": preferences_schema,
    Optional("excluded-dates", drop_if_none=False): Seq(Datetime()) | EmptyList() | EmptyNone(),
    Optional("booked-sessions", drop_if_none=False): Seq(Str()) | EmptyList() | EmptyNone(),
    Optional("watchlist", drop_if_none=False): Seq(Str()) | EmptyList() | EmptyNone(),
    Optional("normalise-venues", drop_if_none=False): Seq(Map({"replace": Str(), "match": Seq(Str())}))
})

class Preference:
    def __init__(self, time_bucket: str=None, day_bucket: str=None, venue: str = None) -> None:
        self.day_bucket = DayBucket[day_bucket.upper()] if day_bucket else None
        self.time_bucket = TimeBucket[time_bucket.upper()] if time_bucket else None
        self.venue = venue or None # don't use Venue class to avoid circular import, to fix later.
        self.date = None # to implement

class Config():
    def __init__(self, values):
        self.watchlist: list[str] = values["watchlist"]
        self.max_sessions: int = values["max-sessions"]
        self.iterations: int = values["iterations"]
        self.preferences: list[Preference] = self.get_preferences(values["preferences"])
        self.excluded_dates: list[date] = values["excluded-dates"]
        self.booked_sessions: list[str] = values["booked-sessions"]
        self.normalise_venues: list[dict[str, str]] = values["normalise-venues"]

    def get_preferences(self, preferences) -> list[Preference]:
        return [
            Preference(
                time_bucket=pref.get("time-bucket"),
                day_bucket=pref.get("day-bucket"),
                venue=pref.get("venue")
            )
            for pref in preferences
        ]

def get_config() -> Config:
    try:
        with open("config.yaml", "r") as file:
            return Config(load(file.read(), schema).data)
    except FileNotFoundError as e:
        raise SystemExit("config.yaml missing. Copy from config.yaml.example and make your changes.") from e

CONFIG = get_config()