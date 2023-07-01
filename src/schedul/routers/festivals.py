from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select

from clients.sql import get_session
from models.festival import Festival, FestivalCreate, FestivalRead, FestivalUpdate
from models.preference import ScheduleRequest
from models.screening import ScoredScreeningRead, Screening, ScreeningRead
from models.user import User
from models.watchlist import WatchlistEntry
from services.schedule import generate_schedule

router = APIRouter(tags=["Festivals"])


@router.get("/festivals/{festival_id}", response_model=FestivalRead)
def get_festival(*, session: Session = Depends(get_session), festival_id: int):
    if festival := session.get(Festival, festival_id):
        return festival
    else:
        raise HTTPException(status_code=404, detail="Festival not found")


@router.get("/festivals", response_model=list[FestivalRead])
def get_festivals(
    *,
    session: Session = Depends(get_session),
    short_name: Annotated[str | None, Query(max_length=50)] = None,
):
    if short_name:
        statement = select(Festival).where(Festival.short_name == short_name)
        return session.exec(statement).all() or Response(status_code=204)
    return session.exec(select(Festival)).all() or Response(status_code=204)


@router.post("/festivals", response_model=FestivalRead, status_code=201)
def create_festival(
    *, session: Session = Depends(get_session), festival: FestivalCreate
):
    db_festival = Festival.from_orm(festival)
    session.add(db_festival)
    session.commit()
    session.refresh(db_festival)
    return db_festival


@router.patch("/festivals/{festival_id}", response_model=FestivalRead)
def update_festival(
    *,
    session: Session = Depends(get_session),
    festival_id: int,
    festival: FestivalUpdate,
):
    if festival_to_update := session.get(Festival, festival_id):
        festival_data = festival.dict(exclude_unset=True)
        for key, value in festival_data.items():
            setattr(festival_to_update, key, value)
        session.add(festival_to_update)
        session.commit()
        session.refresh(festival_to_update)
        return festival_to_update
    else:
        raise HTTPException(status_code=404, detail="Festival not found")


@router.delete("/festivals/{festival_id}")
def delete_festival(*, session: Session = Depends(get_session), festival_id: int):
    if festival := session.get(Festival, festival_id):
        session.delete(festival)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Festival not found")


@router.post(
    "/festivals/{festival_id}/schedule", response_model=list[ScoredScreeningRead]
)
def get_schedule(
    *,
    session: Session = Depends(get_session),
    festival_id: int,
    schedule_request: ScheduleRequest,
):
    if not session.get(Festival, festival_id):
        raise HTTPException(status_code=404, detail="Festival not found")
    if not session.get(User, schedule_request.user_uuid):
        raise HTTPException(status_code=400, detail="User not found")
    screenings = session.exec(
        select(Screening).where(Screening.festival_id == festival_id)
    ).all()
    watchlist_entries = session.exec(
        select(WatchlistEntry).where(
            WatchlistEntry.user_uuid == schedule_request.user_uuid
        )
    ).all()
    watchlist_ids = [watchlist_entry.film_id for watchlist_entry in watchlist_entries]
    return generate_schedule(screenings, schedule_request, watchlist_ids)


@router.get("/festivals/{festival_id}/sessions", response_model=list[ScreeningRead])
def get_sessions(*, session: Session = Depends(get_session), festival_id: int):
    if session.get(Festival, festival_id):
        return session.exec(
            select(Screening).where(Screening.festival_id == festival_id)
        ).all()
    else:
        raise HTTPException(status_code=404, detail="Festival not found")
