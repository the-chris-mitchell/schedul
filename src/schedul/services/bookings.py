import uuid as uuid_pkg

from sqlmodel import Session, select

from models.bookings import Booking, BookingCreate, BookingScreening
from models.screening import Screening


def get_bookings(session: Session, user_uuid: uuid_pkg.UUID):
    return list(
        session.exec(select(Booking).where(Booking.user_uuid == user_uuid)).all()
    )


def get_booking_screenings(
    session: Session, user_uuid: uuid_pkg.UUID
) -> list[BookingScreening]:
    bookings = get_bookings(session=session, user_uuid=user_uuid)

    screenings = session.exec(select(Screening)).all()

    booking_screenings: list[BookingScreening] = []

    for screening in screenings:
        booking_ids = [booking.screening_id for booking in bookings]
        if screening.id in booking_ids:
            booking_screenings.append(
                BookingScreening(screening, screening.film, screening.venue, True)
            )
        else:
            booking_screenings.append(
                BookingScreening(screening, screening.film, screening.venue, False)
            )

    return booking_screenings


def create_booking_db(
    session: Session, user_uuid: uuid_pkg.UUID, screening_id: int
) -> Booking:
    booking = BookingCreate(user_uuid=user_uuid, screening_id=screening_id)
    db_booking = Booking.model_validate(booking)
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


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
