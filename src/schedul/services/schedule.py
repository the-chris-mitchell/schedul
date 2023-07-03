import random
from collections import Counter
from datetime import timedelta

import arrow

from models.preference import ScheduleRequest
from models.screening import ScoredScreening, Screening
from services.screening import get_day_bucket, get_time_bucket


def generate_schedule(
    all_screenings: list[Screening],
    schedule_request: ScheduleRequest,
    watchlist_ids: list[int],
    booked_session_ids: list[int],
) -> list[ScoredScreening]:
    available_screenings = [
        session
        for session in all_screenings
        if arrow.get(session.start_time_utc).to(schedule_request.time_zone).date()
        not in schedule_request.excluded_dates
        or session.id in booked_session_ids
    ]

    watchlist_screenings = [
        screening
        for screening in available_screenings
        if screening.film.id in watchlist_ids or screening.id in booked_session_ids
    ]

    non_watchlist_screenings = [
        screening
        for screening in available_screenings
        if screening.film.id not in watchlist_ids
    ]

    selected_screenings = watchlist_screenings
    if not schedule_request.watchlist_only:
        selected_screenings.extend(non_watchlist_screenings)

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

    schedule: list[ScoredScreening] = []
    scored_screenings: list[ScoredScreening] = []

    # 1. Score the screenings
    for screening in selected_screenings:
        scored_screening = ScoredScreening(
            get_day_bucket(screening.start_time_utc, schedule_request.time_zone),
            get_time_bucket(screening.start_time_utc, schedule_request.time_zone),
            screening=screening,
        )

        if screening.id in booked_session_ids:
            scored_screening.booked = True

        if screening in one_off_watchlist_screenings:
            scored_screening.score = scored_screening.score + 3

        if not schedule_request.watchlist_only and screening.film.id in watchlist_ids:
            scored_screening.score = scored_screening.score + 3

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
                and scored_screening.day_bucket != time_preference.day_bucket
            ):
                continue
            if (
                time_preference.time_bucket
                and scored_screening.time_bucket != time_preference.time_bucket
            ):
                continue
            scored_screening.score = scored_screening.score + (
                len(schedule_request.time_preferences) - position
            )

        scored_screenings.append(scored_screening)

    sorted_scored_screenings: list[ScoredScreening] = sorted(
        scored_screenings, key=lambda item: item.score, reverse=True
    )

    # 2. Add booked sessions first
    schedule.extend(
        scored_screening
        for scored_screening in sorted_scored_screenings
        if scored_screening.booked
    )

    # 3. Attempt to add them in scored order
    schedule.extend(
        scored_screening
        for scored_screening in sorted_scored_screenings
        if should_add(scored_screening.screening, schedule, schedule_request)
    )

    return schedule


def shuffle(screenings: list[Screening]) -> list[Screening]:
    return random.sample(screenings, k=len(screenings))


def should_add(
    screening: Screening,
    schedule: list[ScoredScreening],
    schedule_request: ScheduleRequest,
) -> bool:
    if arrow.get(screening.start_time_utc) < arrow.utcnow():
        return False
    if any(entry.screening.film.name == screening.film.name for entry in schedule):
        return False
    if any(
        entry.screening.start_time_utc
        <= (screening.end_time_utc + timedelta(minutes=schedule_request.buffer_minutes))
        and screening.start_time_utc
        <= (
            entry.screening.end_time_utc
            + timedelta(minutes=schedule_request.buffer_minutes)
        )
        for entry in schedule
    ):
        return False
    return (
        len(
            [
                entry
                for entry in schedule
                if arrow.get(entry.screening.start_time_utc)
                .to(schedule_request.time_zone)
                .date()
                == arrow.get(screening.start_time_utc)
                .to(schedule_request.time_zone)
                .date()
            ]
        )
        < schedule_request.max_daily_sessions
    )
