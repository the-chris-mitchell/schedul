import random
from collections import Counter
from datetime import datetime, timedelta

import arrow
from models.festival import Festival
from models.preference import ScheduleRequest
from models.screening import ScoredScreening, Screening
from services.film import in_watchlist
from services.screening import get_day_bucket, get_time_bucket
from tqdm import tqdm


def generate_schedule(
    screenings: list[Screening], schedule_request: ScheduleRequest, festival: Festival
) -> list[Screening]:
    all_schedules: list[list[Screening]] = []
    watchlist_screenings = [
        screening for screening in screenings if in_watchlist(screening.film)
    ]
    non_watchlist_screenings = [
        screening for screening in screenings if not in_watchlist(screening.film)
    ]

    screenings_per_watchlist_film = Counter(
        session.film.name for session in watchlist_screenings
    )

    single_session_watchlist_films = {
        key for key, value in screenings_per_watchlist_film.items() if value == 1
    }
    one_off_watchlist_screenings = [
        session
        for session in watchlist_screenings
        if session.film.name in single_session_watchlist_films
    ]

    multi_session_watchlist_films = {
        key for key, value in screenings_per_watchlist_film.items() if value > 1
    }
    one_of_many_watchlist_screenings = [
        session
        for session in watchlist_screenings
        if session.film.name in multi_session_watchlist_films
    ]

    # todo
    booked_screenings: list[Screening] = []
    # for session in booked_screenings:
    #     session.book()

    schedule: list[Screening] = booked_screenings

    shuffled_screenings = shuffle(one_off_watchlist_screenings) + shuffle(
        one_of_many_watchlist_screenings
    )

    if not schedule_request.watchlist_only:
        shuffled_screenings.extend(shuffle(non_watchlist_screenings))

    source_screenings = [
        session
        for session in shuffled_screenings
        if session.start_time.date() not in schedule_request.excluded_dates
    ]

    # 1. Score the screenings
    scored_screenings = []
    for screening in source_screenings:
        scored_screening = ScoredScreening(screening=screening)

        for position, venue_name in enumerate(schedule_request.venues, start=0):
            if screening.venue.name == venue_name:
                scored_screening.score = scored_screening.score + (
                    len(schedule_request.venues) - position
                )

        for position, time_preference in enumerate(
            schedule_request.time_preferences, start=0
        ):
            if (
                time_preference.day_bucket
                and get_day_bucket(screening.start_time) != time_preference.day_bucket
            ):
                continue
            if (
                time_preference.time_bucket
                and get_time_bucket(screening.start_time) != time_preference.time_bucket
            ):
                continue
            scored_screening.score = scored_screening.score + (
                len(schedule_request.time_preferences) - position
            )

        scored_screenings.append(scored_screening)

    sorted_scored_screenings: list[ScoredScreening] = sorted(
        scored_screenings, key=lambda item: item.score, reverse=True
    )

    # 2. Attempt to add them in scored order
    for scored_screening in sorted_scored_screenings:
        if should_add(scored_screening.screening, schedule, schedule_request):
            schedule.append(scored_screening.screening)

    return schedule


def shuffle(screenings: list[Screening]) -> list[Screening]:
    return random.sample(screenings, k=len(screenings))


def should_add(
    screening: Screening, schedule: list[Screening], schedule_request: ScheduleRequest
) -> bool:
    if arrow.get(screening.start_time) < arrow.utcnow():
        return False
    if any(entry.film.name == screening.film.name for entry in schedule):
        return False
    if any(
        entry.start_time
        <= (screening.end_time + timedelta(minutes=schedule_request.buffer_minutes))
        and screening.start_time
        <= (entry.end_time + timedelta(minutes=schedule_request.buffer_minutes))
        for entry in schedule
    ):
        return False
    return (
        len(
            [
                entry
                for entry in schedule
                if entry.start_time.date() == screening.start_time.date()
            ]
        )
        < schedule_request.max_daily_sessions
    )


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
