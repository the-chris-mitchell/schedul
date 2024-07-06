import uuid as uuid_pkg

from sqlmodel import Session, select

from models.bookings import Booking, BookingCreate, BookingScreening
from models.screening import ScreeningPublic
from services.screening import get_screenings_db


def create_booking_db(session: Session, booking: BookingCreate) -> Booking:
    db_booking = Booking.model_validate(booking)
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


def create_booking_if_required_db(
    session: Session, booking: BookingCreate
) -> tuple[Booking, bool]:
    if response := session.exec(
        select(Booking)
        .where(Booking.user_uuid == booking.user_uuid)
        .where(Booking.screening_id == booking.screening_id)
    ).first():
        return (response, False)
    else:
        return (create_booking_db(session=session, booking=booking), True)


def delete_booking_db(
    session: Session, user_uuid: uuid_pkg.UUID, screening_id: int
) -> bool:
    if bookings := session.exec(
        select(Booking)
        .where(Booking.user_uuid == user_uuid)
        .where(Booking.screening_id == screening_id)
    ).all():
        for booking in bookings:
            session.delete(booking)
            session.commit()
        return True
    return False


def get_bookings_db(session: Session, user_uuid: uuid_pkg.UUID):
    return list(
        session.exec(select(Booking).where(Booking.user_uuid == user_uuid)).all()
    )


def get_booking_screenings(
    session: Session, user_uuid: uuid_pkg.UUID
) -> list[BookingScreening]:
    bookings = get_bookings_db(session=session, user_uuid=user_uuid)

    screenings = get_screenings_db(session=session)

    booking_screenings: list[BookingScreening] = []

    for screening in screenings:
        booking_ids = [booking.screening_id for booking in bookings]
        screening_public = ScreeningPublic.model_validate(screening)
        if screening.id in booking_ids:
            booking_screenings.append(
                BookingScreening(screening=screening_public, is_booked=True)
            )
        else:
            booking_screenings.append(
                BookingScreening(screening=screening_public, is_booked=False)
            )

    return booking_screenings
