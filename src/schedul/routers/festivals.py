from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlmodel import select
from clients.sql import get_session

from models.festival import FestivalCreate, FestivalRead, Festival, FestivalUpdate
from models.screening import Screening
from services.schedule import generate_schedule


router = APIRouter(tags=["Festivals"])


@router.get("/festivals/{festival_id}", response_model=FestivalRead)
def get_festival(*, session: Session = Depends(get_session), festival_id: int):
    if festival := session.get(Festival, festival_id):
        return festival
    else:
        raise HTTPException(status_code=404, detail="Festival not found")

@router.get("/festivals", response_model=list[FestivalRead])
def get_festivals(*, session: Session = Depends(get_session)):
    return session.exec(select(Festival)).all()

@router.post("/festivals", response_model=FestivalRead, status_code=201)
def create_festival(*, session: Session = Depends(get_session), festival: FestivalCreate):
    db_festival = Festival.from_orm(festival)
    session.add(db_festival)
    session.commit()
    session.refresh(db_festival)
    return db_festival

@router.patch("/festivals/{festival_id}", response_model=FestivalRead)
def update_festival(*, session: Session = Depends(get_session), festival_id: int, festival: FestivalUpdate):
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

@router.get("/festivals/{festival_id}/schedule", response_model=list[str])
def get_schedule(*, session: Session = Depends(get_session), festival_id: int):
    if session.get(Festival, festival_id):
        screenings = session.exec(select(Screening).where(Screening.festival_id == festival_id)).all()
        return generate_schedule(screenings)
    else:
        raise HTTPException(status_code=404, detail="Festival not found")