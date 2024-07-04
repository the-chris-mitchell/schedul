import io
import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from ics import Calendar, Event
from sqlmodel import Session, select

from clients.sql import get_session
from models.bookings import Booking, Bookings
from models.screening import Screening
from models.user import User
from services.bookings import (
    create_booking_db,
    delete_booking_db,
    get_booking_screenings,
)

router = APIRouter(tags=["Users"])


@router.delete("/users/{user_uuid}/bookings/{screening_id}")
def delete_booking(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
    screening_id: int,
) -> dict[str, bool]:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if delete_booking_db(
        session=session, user_uuid=user_uuid, screening_id=screening_id
    ):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Booking not found")


@router.put(
    "/users/{user_uuid}/bookings/{screening_id}",
    responses={201: {"model": Booking}, 202: {"model": Booking}},
)
def create_booking(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
    screening_id: int,
) -> JSONResponse:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if not session.get(Screening, screening_id):
        raise HTTPException(status_code=404, detail="Screening not found")

    if existing_booking := session.exec(
        select(Booking)
        .where(Booking.user_uuid == user_uuid)
        .where(Booking.screening_id == screening_id)
    ).first():
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=jsonable_encoder(existing_booking),
        )

    booking = create_booking_db(
        session=session, user_uuid=user_uuid, screening_id=screening_id
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(booking)
    )


@router.get(
    "/users/{user_uuid}/bookings",
    response_model=Bookings,
)
def get_bookings(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
) -> Bookings:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    return Bookings(get_booking_screenings(session=session, user_uuid=user_uuid))


@router.get(
    "/users/{user_uuid}/bookings.ics",
)
async def get_bookings_ics(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
):
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    screenings = get_booking_screenings(session=session, user_uuid=user_uuid)

    calendar = Calendar()
    for screening in screenings:
        if screening.is_booked:
            event = Event()
            event.name = screening.film.name
            event.begin = screening.screening.start_time_utc
            event.end = screening.screening.end_time_utc
            event.location = screening.screening.venue.name
            calendar.events.add(event)

    content = io.BytesIO(calendar.serialize().encode())

    return StreamingResponse(content, media_type="text/calendar")
