from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from clients.sql import get_session
from models.screening import Screening, ScreeningCreate, ScreeningPublic
from services.screening import (
    create_screening_db,
    delete_screening_db,
    get_screenings_db,
)

router = APIRouter(tags=["Screening"])


@router.get("/screenings/{screening_id}", response_model=ScreeningPublic)
def get_screening(*, session: Session = Depends(get_session), screening_id: int):
    if screening := session.get(Screening, screening_id):
        return screening
    else:
        raise HTTPException(status_code=404, detail="Screening not found")


@router.get("/screenings", response_model=list[ScreeningPublic])
def get_screenings(*, session: Session = Depends(get_session)):
    return get_screenings_db(session=session)


@router.post("/screenings", response_model=ScreeningPublic, status_code=201)
def create_screening(
    *, session: Session = Depends(get_session), screening: ScreeningCreate
):
    return create_screening_db(session=session, screening=screening)


@router.delete("/screenings/{screening_id}")
def delete_screening(*, session: Session = Depends(get_session), screening_id: int):
    if delete_screening_db(session=session, screening_id=screening_id):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Screening not found")
