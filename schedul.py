import argparse
from datetime import date
from models.enums import DayBucket, TimeBucket

from festivals.fff import get_sessions as get_fff_sessions
from models.options import Options
from models.preference import Preference
from models.schedule import Schedule
from models.session import Session
from models.venue import Venue
from festivals.nziff import get_sessions as get_nziff_sessions
from process import get_schedule

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=['print', 'calendar'], help="What mode to run")
parser.add_argument("festival", choices=['fff', 'nziff'], help="Specify Festival")
args = parser.parse_args()


MAX_SESSIONS: int = 2
ITERATIONS: int = 100

PREFERENCES: list[Preference] = [
    Preference(venue=Venue("Embassy Theatre The Grand")),
    Preference(TimeBucket.MORNING, DayBucket.WEEKEND, venue=Venue("Light House Cuba")),
    Preference(TimeBucket.AFTERNOON, DayBucket.WEEKEND, venue=Venue("Light House Cuba")),
    Preference(TimeBucket.MORNING, DayBucket.WEEKEND),
    Preference(TimeBucket.AFTERNOON, DayBucket.WEEKEND),
    Preference(TimeBucket.EVENING, DayBucket.WEEKEND),
    Preference(TimeBucket.EVENING, DayBucket.FRIDAY),
    Preference(TimeBucket.EVENING, DayBucket.WEEKDAY),
]

EXCLUDED_DATES: list[date] = [
    date(2022, 6, 10), # Parents visiting weekend
    date(2022, 6, 11), # Parents visiting weekend
    date(2022, 6, 12), # Parents visiting weekend
    date(2022, 6, 13), # Wellington Film Society
    date(2022, 6, 20), # Wellington Film Society
]

BOOKED_LINKS: list[str] = [
    "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633596&bookingSource=www|movies",
    "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633599&bookingSource=www|movies",
    "https://ticketing.oz.veezi.com/purchase/85571?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85561?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85575?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85173?siteToken=1qejxwctrta7sf1x8th102760g"
]

options = Options(ITERATIONS, MAX_SESSIONS, PREFERENCES, EXCLUDED_DATES, BOOKED_LINKS)


schedule: Schedule

match args.festival:
    case "fff":
        schedule = get_schedule(options, get_fff_sessions(), "French Film Festival")
    case "nziff":
        schedule = get_schedule(options, get_nziff_sessions(), "Whānau Mārama: NZIFF")

match args.mode:
    case "print":
        print(schedule.get_formatted())
    case "calendar":
        schedule.save_calendar("movies.ics")
