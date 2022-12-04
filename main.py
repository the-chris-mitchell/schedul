from datetime import date, timedelta
from get_data import get_sessions

from tqdm import tqdm

import random

from models import DayBucket, Preference, Schedule, Session, TimeBucket, Venue

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

BOOKED: list[str] = [
    "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633596&bookingSource=www|movies",
    "https://www.eventcinemas.co.nz/Orders/Tickets#sessionId=1633599&bookingSource=www|movies",
    "https://ticketing.oz.veezi.com/purchase/85571?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85561?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85575?siteToken=jjyv8y2k8xe3rn5wxqrp2pym64",
    "https://ticketing.oz.veezi.com/purchase/85173?siteToken=1qejxwctrta7sf1x8th102760g"
]

def valid_session(session: Session, schedule: Schedule):
    if len(schedule.sessions) == 0:
        return True
    if session.start_time.date() in EXCLUDED_DATES:
        return False
    if any(entry.film.name == session.film.name for entry in schedule.sessions):
        return False
    if any(entry.start_time <= (session.end_time + timedelta(minutes=30)) and session.start_time <= (entry.end_time + timedelta(minutes=30)) for entry in schedule.sessions):
        return False
    if len([x for x in schedule.sessions if x.start_time.date() == session.start_time.date()]) == MAX_SESSIONS:
        return False
    return True

sessions: list[Session] = get_sessions()

all_schedules: list[Schedule] = []

for x in tqdm(range(ITERATIONS)):

    current_schedule = Schedule()

    booked_sessions = [session for session in sessions if session.link in BOOKED]

    [session.book() for session in booked_sessions]

    current_schedule.sessions.extend(booked_sessions)

    shuffled_sessions: list[Session] = random.sample(sessions, k=len(sessions))

    for preference in PREFERENCES:
        for session in shuffled_sessions:
            if preference.date and session.start_time.date() != preference.date:
                continue
            if preference.day_bucket and session.day_bucket != preference.day_bucket:
                continue
            if preference.time_bucket and session.time_bucket != preference.time_bucket:
                continue
            if preference.venue and session.venue.name != preference.venue.name:
                continue
            if valid_session(session, current_schedule):
                current_schedule.sessions.append(session)

    all_schedules.append(current_schedule)

best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(PREFERENCES), reverse=True)[0]

print(f"🎬 Generated a schedule with {len(best_schedule.sessions)} films:")

sorted_best_schedule: Schedule = sorted(best_schedule.sessions, key=lambda x: x.start_time)

for position, week in enumerate(sorted(list(set([session.start_time.isocalendar()[1] for session in sorted_best_schedule]))), start=1):
    print(f"\n📆 Week {position}:")
    print("─" * 10)
    for session in [session for session in sorted_best_schedule if session.start_time.isocalendar()[1] == week]:
        print(session.format())
        if not session.booked:
            print(f"↪️ 🔗 {session.link}")
