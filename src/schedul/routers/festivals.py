from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from schedul.clients.sql import get_session
from schedul.models.festival import FestivalCreate, FestivalPublic
from schedul.models.preference import ScheduleRequest
from schedul.models.screening import ScoredScreening, ScreeningPublic
from schedul.services.festival import (
    create_festival_db,
    delete_festival_db,
    get_festival_db,
    get_festivals_db,
)
from schedul.services.schedule import get_festival_schedule
from schedul.services.screening import get_festival_screenings_db
from schedul.services.users import get_user_db

router = APIRouter(tags=["Festivals"])


@router.get("/festivals/{festival_id}", response_model=FestivalPublic)
def get_festival(*, session: Session = Depends(get_session), festival_id: int):
    if festival := get_festival_db(session=session, festival_id=festival_id):
        return festival
    else:
        raise HTTPException(status_code=404, detail="Festival not found")


@router.get("/festivals", response_model=list[FestivalPublic])
def get_festivals(
    *,
    session: Session = Depends(get_session),
    short_name: Annotated[str | None, Query(max_length=50)] = None,
):
    return get_festivals_db(session=session, short_name=short_name) or Response(
        status_code=204
    )


@router.post("/festivals", response_model=FestivalPublic, status_code=201)
def create_festival(
    *, session: Session = Depends(get_session), festival: FestivalCreate
):
    return create_festival_db(session=session, festival=festival)


@router.delete("/festivals/{festival_id}")
def delete_festival(*, session: Session = Depends(get_session), festival_id: int):
    if delete_festival_db(session=session, festival_id=festival_id):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Festival not found")


@router.post("/festivals/{festival_id}/schedule", response_model=list[ScoredScreening])
def get_schedule(
    *,
    session: Session = Depends(get_session),
    festival_id: int,
    schedule_request: ScheduleRequest,
):
    if not get_festival_db(session=session, festival_id=festival_id):
        raise HTTPException(status_code=404, detail="Festival not found")
    if not get_user_db(session=session, user_uuid=schedule_request.user_uuid):
        raise HTTPException(status_code=400, detail="User not found")

    if len(schedule_request.venue_preferences) == 0:
        raise HTTPException(
            status_code=400, detail="Must include at least one venue preference"
        )

    return get_festival_schedule(
        session=session, festival_id=festival_id, schedule_request=schedule_request
    )


@router.get("/festivals/{festival_id}/screenings", response_model=list[ScreeningPublic])
def get_festival_screenings(
    *, session: Session = Depends(get_session), festival_id: int
):
    if get_festival_db(session=session, festival_id=festival_id):
        return get_festival_screenings_db(session=session, festival_id=festival_id)
    else:
        raise HTTPException(status_code=404, detail="Festival not found")
