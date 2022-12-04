from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlmodel import select # type: ignore
from clients.sql import get_session

from models.venue import VenueCreate, VenueRead, Venue


router = APIRouter(tags=["Venues"])


@router.get("/venues/{venue_id}", response_model=VenueRead)
def get_venue(*, session: Session = Depends(get_session), venue_id: int):
    if venue := session.get(Venue, venue_id):
        return venue
    else:
        raise HTTPException(status_code=404, detail="Venue not found")

@router.get("/venues", response_model=list[VenueRead])
def get_films(*, session: Session = Depends(get_session)):
    return session.exec(select(Venue)).all()

@router.post("/venues", response_model=VenueRead, status_code=201)
def create_venue(*, session: Session = Depends(get_session), venue: VenueCreate):
    db_venue = Venue.from_orm(venue)
    session.add(db_venue)
    session.commit()
    session.refresh(db_venue)
    return db_venue

@router.delete("/venues/{venue_id}")
def delete_venue(*, session: Session = Depends(get_session), venue_id: int):
    if venue := session.get(Venue, venue_id):
        session.delete(venue)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Venue not found")