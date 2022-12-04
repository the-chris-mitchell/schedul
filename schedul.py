import argparse
from datetime import date

from strictyaml import (Datetime, EmptyList, EmptyNone, Enum,  # type: ignore
                        Int, Map, Optional, Seq, Str, load)
from festivals import get_festivals

from models.enums import DayBucket, TimeBucket
from models.options import Options
from models.preference import Preference
from models.schedule import Schedule, get_schedule


festivals = get_festivals()

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=['print', 'cal'], help="What mode to run")
parser.add_argument("festival", choices=[festival.short_name for festival in festivals], help="Specify Festival")
args = parser.parse_args()

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
    Optional("booked-sessions", drop_if_none=False): Seq(Str()) | EmptyList() | EmptyNone()
})

try:
    with open("config.yaml", "r") as file:
        config = load(file.read(), schema).data
except FileNotFoundError:
    raise SystemExit("config.yaml missing. Copy from config.yaml.example and make your changes.")


MAX_SESSIONS: int = config["max-sessions"]
ITERATIONS: int = config["iterations"]

EXCLUDED_DATES: list[date] = [day.date() for day in config["excluded-dates"]]

PREFERENCES: list[Preference] = [
    Preference(
        time_bucket=pref.get("time-bucket"),
        day_bucket=pref.get("day-bucket"),
        venue=pref.get("venue")
    )
    for pref in config["preferences"]
]

BOOKED_SESSIONS: list[str] = config["booked-sessions"]

options = Options(ITERATIONS, MAX_SESSIONS, PREFERENCES, EXCLUDED_DATES, BOOKED_SESSIONS)

schedule: Schedule


selected_festival = [festival for festival in festivals if festival.short_name == args.festival][0]

schedule = get_schedule(options, selected_festival.sessions, selected_festival.full_name)

match args.mode:
    case "print":
        print(schedule.get_formatted())
    case "cal":
        schedule.save_calendar(f"{args.festival}.ics")
