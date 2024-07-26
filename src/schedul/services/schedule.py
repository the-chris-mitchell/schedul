import random
from collections import Counter
from datetime import timedelta

import arrow
from sqlmodel import Session

from schedul.models.preference import ScheduleRequest
from schedul.models.screening import ScoredScreening, Screening, ScreeningPublic
from schedul.services.bookings import get_bookings_db
from schedul.services.screening import get_festival_screenings_db
from schedul.services.venue import get_venues_db
from schedul.services.watchlist import get_watchlist_entries_db


def get_festival_schedule(
    session: Session, festival_id: int, schedule_request: ScheduleRequest
):
    screenings = get_festival_screenings_db(session=session, festival_id=festival_id)

    watchlist_entries = get_watchlist_entries_db(
        session=session, user_uuid=schedule_request.user_uuid
    )

    watchlist_ids = [watchlist_entry.film_id for watchlist_entry in watchlist_entries]

    bookings = get_bookings_db(session=session, user_uuid=schedule_request.user_uuid)
    booked_session_ids = [booking.screening_id for booking in bookings]

    venues = []
    [
        venues.extend(get_venues_db(session=session, venue_name=venue.venue_name))
        for venue in schedule_request.venue_preferences
    ]
    venue_ids = [venue.id for venue in venues if venue.id is not None]

    return generate_schedule(
        screenings, schedule_request, watchlist_ids, booked_session_ids, venue_ids
    )


def generate_schedule(
    all_screenings: list[Screening],
    schedule_request: ScheduleRequest,
    watchlist_ids: list[int],
    booked_session_ids: list[int],
    venue_ids: list[int],
) -> list[ScoredScreening]:
    available_screenings = [
        session
        for session in all_screenings
        if arrow.get(session.start_time_utc).to(schedule_request.time_zone).date()
        not in schedule_request.excluded_dates
        or session.id in booked_session_ids
    ]

    booked_screenings = [
        screening
        for screening in available_screenings
        if screening.id in booked_session_ids
    ]

    watchlist_screenings = [
        screening
        for screening in available_screenings
        if screening.film.id in watchlist_ids and screening.id not in booked_session_ids
    ]

    non_watchlist_screenings = [
        screening
        for screening in available_screenings
        if screening.film.id not in watchlist_ids
        and screening.id not in booked_session_ids
    ]

    selected_screenings = booked_screenings
    selected_screenings.extend(watchlist_screenings)
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
            day_bucket=screening.get_day_bucket(time_zone=schedule_request.time_zone),
            time_bucket=screening.get_time_bucket(time_zone=schedule_request.time_zone),
            screening=ScreeningPublic.model_validate(screening),
        )

        if screening.id in booked_session_ids:
            scored_screening.booked = True

        if screening.film.id in watchlist_ids:
            scored_screening.in_watchlist = True

        if screening in one_off_watchlist_screenings:
            scored_screening.score = scored_screening.score + 3

        if not schedule_request.watchlist_only and screening.film.id in watchlist_ids:
            scored_screening.score = scored_screening.score + 3

        for venue_preference in schedule_request.venue_preferences:
            if screening.venue.name == venue_preference.venue_name:
                scored_screening.score = scored_screening.score + venue_preference.score

        for time_preference in schedule_request.time_preferences:
            if (
                scored_screening.day_bucket == time_preference.day_bucket
                and scored_screening.time_bucket == time_preference.time_bucket
            ):
                scored_screening.score = scored_screening.score + time_preference.score

        scored_screenings.append(scored_screening)

    sorted_scored_screenings: list[ScoredScreening] = sorted(
        scored_screenings, key=lambda item: item.score, reverse=True
    )

    # 2. Add booked screenings first
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
        and scored_screening.screening.venue_id in venue_ids
        and not scored_screening.booked
    )

    return sorted(schedule, key=lambda item: item.screening.start_time_utc)


def shuffle(screenings: list[Screening]) -> list[Screening]:
    return random.sample(screenings, k=len(screenings))


def should_add(
    screening: ScreeningPublic,
    schedule: list[ScoredScreening],
    schedule_request: ScheduleRequest,
) -> bool:
    if (
        schedule_request.future_only
        and arrow.get(screening.start_time_utc) < arrow.utcnow()
    ):
        return False
    if any(entry.screening.film.id == screening.film.id for entry in schedule):
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
        < schedule_request.max_daily_screenings
    )
