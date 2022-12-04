
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from yaml import Loader, load # type: ignore

from models.enums import DayBucket, TimeBucket


class Preference(BaseModel):
    day_bucket: Optional[DayBucket]
    time_bucket: Optional[TimeBucket]
    venue: Optional[str]
    date: Optional[str]

class NormalisedVenue(BaseModel):
    replace: str
    match: list[str]

class Config(BaseModel):
    max_sessions: int
    iterations: int
    buffer_time: int
    preferences: list[Preference]
    excluded_dates: list[date] = Field(default_factory=list)
    booked_sessions: list[str] = Field(default_factory=list)
    normalise_venues: list[NormalisedVenue] = Field(default_factory=list)
    watchlist: list[str] = Field(default_factory=list)

def get_config() -> Config:
    try:
        with open("../../config.yaml", "r") as file:
            data = load(file, Loader=Loader)
            return Config.parse_obj(data)
    except FileNotFoundError as e:
        raise SystemExit("config.yaml missing. Copy from config.yaml.example and make your changes.") from e

CONFIG = get_config()