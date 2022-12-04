from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlmodel import select # type: ignore
from clients.sql import get_session

from models.screening import ScreeningCreate, ScreeningRead, Screening


router = APIRouter(tags=["Screening"])


@router.get("/screenings/{screening_id}", response_model=ScreeningRead)
def get_screening(*, session: Session = Depends(get_session), screening_id: int):
    if screening := session.get(Screening, screening_id):
        return screening
    else:
        raise HTTPException(status_code=404, detail="Screening not found")

@router.get("/screenings", response_model=list[ScreeningRead])
def get_screenings(*, session: Session = Depends(get_session)):
    return session.exec(select(Screening)).all()

@router.post("/screenings", response_model=ScreeningRead, status_code=201)
def create_screening(*, session: Session = Depends(get_session), screening: ScreeningCreate):
    db_screening = Screening.from_orm(screening)
    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)
    return db_screening

@router.delete("/screenings/{screening_id}")
def delete_screening(*, session: Session = Depends(get_session), screening_id: int):
    if screening := session.get(Screening, screening_id):
        session.delete(screening)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Screening not found")