import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from clients.sql import get_session
from models.bookings import Booking, BookingCreate, Bookings, BookingScreening
from models.screening import Screening
from models.user import User

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

    if booking := session.exec(
        select(Booking)
        .where(Booking.user_uuid == user_uuid)
        .where(Booking.screening_id == screening_id)
    ).first():
        session.delete(booking)
        session.commit()
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

    booking = BookingCreate(user_uuid=user_uuid, screening_id=screening_id)
    db_booking = Booking.from_orm(booking)
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(db_booking)
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

    bookings = session.exec(select(Booking).where(Booking.user_uuid == user_uuid)).all()

    screenings = session.exec(select(Screening)).all()

    booking_screenings = []

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

    return Bookings(booking_screenings)