import io
import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from ics import Calendar, Event
from sqlmodel import Session

from clients.sql import get_session
from models.bookings import Booking, BookingCreate, BookingScreening
from models.user import User
from services.bookings import (
    create_booking_if_required_db,
    delete_booking_db,
    get_booking_screenings,
)
from services.screening import get_screening_db
from services.users import get_user_db

router = APIRouter(tags=["Users"])


@router.delete("/users/{user_uuid}/bookings/{screening_id}")
def delete_booking(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
    screening_id: int,
) -> dict[str, bool]:
    if not get_user_db(session=session, user_uuid=user_uuid):
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
    if not get_user_db(session=session, user_uuid=user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if not get_screening_db(session=session, screening_id=screening_id):
        raise HTTPException(status_code=404, detail="Screening not found")

    booking, created = create_booking_if_required_db(
        session=session,
        booking=BookingCreate(user_uuid=user_uuid, screening_id=screening_id),
    )
    if created:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(booking)
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED, content=jsonable_encoder(booking)
        )


@router.get(
    "/users/{user_uuid}/bookings",
    response_model=list[BookingScreening],
)
def get_bookings(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
) -> list[BookingScreening]:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    return get_booking_screenings(session=session, user_uuid=user_uuid)


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
            event.name = screening.screening.film.name
            event.begin = screening.screening.start_time_utc
            event.end = screening.screening.end_time_utc
            event.location = screening.screening.venue.name
            calendar.events.add(event)

    content = io.BytesIO(calendar.serialize().encode())

    return StreamingResponse(content, media_type="text/calendar")
