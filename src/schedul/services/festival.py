from sqlmodel import Session, select

from clients.sql import engine
from models.festival import Festival
from models.preference import ScheduleRequest
from models.screening import Screening
from services.bookings import get_bookings
from services.schedule import generate_schedule
from services.venue import get_venues_db
from services.watchlist import get_watchlist_entries_db


def create_festival(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        db_festival = Festival(full_name=full_name, short_name=short_name)
        session.add(db_festival)
        session.commit()
        session.refresh(db_festival)
        return db_festival


def create_festival_if_required(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        query = session.exec(
            select(Festival).where(Festival.short_name == short_name)
        ).first()
        return query or create_festival(full_name=full_name, short_name=short_name)


def get_sessions_db(session: Session, festival_id) -> list[Screening]:
    return list(
        session.exec(
            select(Screening).where(Screening.festival_id == festival_id)
        ).all()
    )


def get_festival_schedule_db(
    session: Session, festival_id: int, schedule_request: ScheduleRequest
):
    screenings = get_sessions_db(session=session, festival_id=festival_id)

    watchlist_entries = get_watchlist_entries_db(
        session=session, user_uuid=schedule_request.user_uuid
    )

    watchlist_ids = [watchlist_entry.film_id for watchlist_entry in watchlist_entries]

    bookings = get_bookings(session=session, user_uuid=schedule_request.user_uuid)
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
