import uuid as uuid_pkg

from sqlmodel import Session, select

from models.bookings import Booking, BookingScreening
from models.screening import Screening


def get_booking_screenings(
    user_uuid: uuid_pkg.UUID, session: Session
) -> list[BookingScreening]:
    bookings = session.exec(select(Booking).where(Booking.user_uuid == user_uuid)).all()

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
