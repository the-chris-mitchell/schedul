import random
from collections import Counter
from datetime import datetime

import arrow
from models.screening import Screening
from services.film import in_watchlist
from services.screening import get_day_bucket, get_time_bucket
from tqdm import tqdm


def generate_schedule(screenings: list[Screening]) -> list[Screening]:
    all_schedules: list[list[Screening]] = []
    watchlist_sessions = [
        screening for screening in screenings if in_watchlist(screening.film)
    ]
    non_watchlist_sessions = [
        screening for screening in screenings if not in_watchlist(screening.film)
    ]

    sessions_per_watchlist_film = Counter(
        session.film.name for session in watchlist_sessions
    )

    single_session_watchlist_films = {
        key for key, value in sessions_per_watchlist_film.items() if value == 1
    }
    one_off_watchlist_sessions = [
        session
        for session in watchlist_sessions
        if session.film.name in single_session_watchlist_films
    ]

    multi_session_watchlist_films = {
        key for key, value in sessions_per_watchlist_film.items() if value > 1
    }
    one_of_many_watchlist_sessions = [
        session
        for session in watchlist_sessions
        if session.film.name in multi_session_watchlist_films
    ]

    # booked_sessions = [screening for screening in screenings if screening.id in CONFIG.booked_sessions]
    booked_sessions: list[Screening] = []

    # for session in booked_sessions:
    #     session.book()

    iterations: int = 1

    for _ in tqdm(range(iterations), leave=False, unit="schedule"):
        current_schedule: list[Screening] = []

        current_schedule.extend(booked_sessions)

        shuffled_sessions = shuffle(one_off_watchlist_sessions) + shuffle(
            one_of_many_watchlist_sessions
        )  # + shuffle(non_watchlist_sessions)

        # for preference in CONFIG.preferences:
        #     for session in shuffled_sessions:
        #         if preference.date and session.start_time.date() != preference.date:
        #             continue
        #         if preference.day_bucket and get_day_bucket(session.start_time) != preference.day_bucket:
        #             continue
        #         if preference.time_bucket and get_time_bucket(session.start_time) != preference.time_bucket:
        #             continue
        #         if preference.venue and session.venue.name != preference.venue:
        #             continue
        #         if should_add(session, current_schedule):
        #             current_schedule.append(session)

        #         # current_schedule.try_add_session(session)

        for session in shuffled_sessions:
            if should_add(session, current_schedule):
                current_schedule.append(session)

        all_schedules.append(current_schedule)

    best_schedule: list[Screening] = sorted(
        all_schedules, key=lambda item: calculate_score(item), reverse=True
    )[0]

    return sorted(best_schedule, key=lambda x: x.start_time)


def shuffle(screenings: list[Screening]) -> list[Screening]:
    return random.sample(screenings, k=len(screenings))


def calculate_score(screenings: list[Screening]) -> float:
    score: float = 0
    # for position, preference in enumerate(CONFIG.preferences, start=1):
    #     position_score = 0
    #     if preference.date:
    #         position_score += len([session for session in screenings if session.start_time.date() == preference.date])
    #     if preference.day_bucket:
    #         position_score += len([session for session in screenings if get_day_bucket(session.start_time) == preference.day_bucket])
    #     if preference.time_bucket:
    #         position_score += len([session for session in screenings if get_time_bucket(session.start_time) == preference.time_bucket])
    #     if preference.venue:
    #         position_score += len([session for session in screenings if session.venue.name == preference.venue])

    #     score += position_score / position

    return score


def should_add(screening: Screening, schedule: list[Screening]) -> bool:
    # if arrow.get(screening.start_time) < arrow.utcnow():
    #     return False
    # if screening.start_time.date() in CONFIG.excluded_dates:
    #     return False
    # if any(entry.film.name == screening.film.name for entry in schedule):
    #     return False
    # if any(entry.start_time <= (screening.end_time + timedelta(minutes=CONFIG.buffer_time)) and screening.start_time <= (entry.end_time + timedelta(minutes=CONFIG.buffer_time)) for entry in schedule):
    #     return False
    # if len([x for x in schedule if x.start_time.date() == screening.start_time.date()]) >= CONFIG.max_sessions:
    #     return False
    return True


def start_time_formatted(screening: Screening) -> str:
    return datetime.fromisoformat(str(screening.start_time)).strftime(
        f"%a {get_time_bucket(screening.start_time).name.capitalize()} (%d/%m) %I:%M%p"
    )


def end_time_formatted(screening: Screening) -> str:
    return datetime.fromisoformat(str(screening.end_time)).strftime("%I:%M%p")


# def get_booked_schedule(self) -> Schedule:
#     booked_sessions = [session for session in self.sessions if session.id in CONFIG.booked_sessions]
#     for session in booked_sessions:
#         session.book()
#     schedule = Schedule()
#     schedule.sessions.extend(booked_sessions)
#     return schedule
