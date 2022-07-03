import argparse
from datetime import date

from strictyaml import (Datetime, EmptyList, EmptyNone, Enum,  # type: ignore
                        Int, Map, Optional, Seq, Str, load)
from festivals import get_festivals

from models.enums import DayBucket, TimeBucket
from models.festival import Festival
from models.options import Options
from models.preference import Preference


festivals = get_festivals()

parser = argparse.ArgumentParser()
parser.add_argument("festival", choices=[festival.short_name for festival in festivals], help="Select a festival")
parser.add_argument("mode", choices=['sessions', 'schedule', 'films', 'csv', 'cal'], help="What mode to run")
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

selected_festival: Festival = [festival for festival in festivals if festival.short_name == args.festival][0]
selected_festival.get_sessions()

match args.mode:
    case "schedule":
        print("=" * 20, f"🎬 {selected_festival.full_name} schedule", "=" * 20)
        print(selected_festival.get_schedule(options).get_formatted())
    case "sessions":
        print("=" * 20, f"🎬 {selected_festival.full_name} sessions", "=" * 20)
        print(selected_festival.get_formatted_sessions())
    case "films":
        print("=" * 20, f"🎬 {selected_festival.full_name} films", "=" * 20)
        print(selected_festival.get_formatted_films())
    case "csv":
        selected_festival.save_films_csv()
    case "cal":
        selected_festival.get_schedule(options).save_calendar(f"{args.festival}.ics")
