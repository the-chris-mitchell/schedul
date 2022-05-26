from datetime import timedelta
import random
from tqdm import tqdm # type: ignore
from models import Options, Schedule, Session


def valid_session(session: Session, schedule: Schedule, options: Options):
    if len(schedule.sessions) == 0:
        return True
    if session.start_time.date() in options.excluded_dates:
        return False
    if any(entry.film.name == session.film.name for entry in schedule.sessions):
        return False
    if any(entry.start_time <= (session.end_time + timedelta(minutes=30)) and session.start_time <= (entry.end_time + timedelta(minutes=30)) for entry in schedule.sessions):
        return False
    if len([x for x in schedule.sessions if x.start_time.date() == session.start_time.date()]) == options.max_sessions:
        return False
    return True

def get_schedule(options: Options, sessions: list[Session], festival: str) -> Schedule:

    all_schedules: list[Schedule] = []

    for x in tqdm(range(options.iterations)):

        current_schedule = Schedule(festival)

        booked_sessions = [session for session in sessions if session.link in options.booked_links]

        for session in booked_sessions:
            session.book()

        current_schedule.sessions.extend(booked_sessions)

        shuffled_sessions: list[Session] = random.sample(sessions, k=len(sessions))

        for preference in options.preferences:
            for session in shuffled_sessions:
                if preference.date and session.start_time.date() != preference.date:
                    continue
                if preference.day_bucket and session.day_bucket != preference.day_bucket:
                    continue
                if preference.time_bucket and session.time_bucket != preference.time_bucket:
                    continue
                if preference.venue and session.venue.name != preference.venue.name:
                    continue
                if valid_session(session, current_schedule, options):
                    current_schedule.sessions.append(session)

        all_schedules.append(current_schedule)

    best_schedule: Schedule = sorted(all_schedules, key=lambda item: item.calculate_score(options.preferences), reverse=True)[0]

    best_schedule.sort()

    return best_schedule

def print_schedule(schedule: Schedule):
    print("=" * 50)
    print(f"🎬 Schedule for {schedule.festival} with {len(schedule.sessions)} films:")
    print("=" * 50)
    for position, week in enumerate(sorted(list(set([session.start_time.isocalendar()[1] for session in schedule.sessions]))), start=1):
        print(f"\n📆 Week {position}:")
        print("─" * 10)
        for session in [session for session in schedule.sessions if session.start_time.isocalendar()[1] == week]:
            print(session.format())
            if not session.booked:
                print(f"↪️ 🔗 {session.link}")