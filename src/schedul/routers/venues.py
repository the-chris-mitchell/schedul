from typing import Annotated

from clients.sql import get_session
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from models.venue import Venue, VenueCreate, VenueRead
from sqlmodel import Session, select

router = APIRouter(tags=["Venues"])


@router.get("/venues/{venue_id}", response_model=VenueRead)
def get_venue(*, session: Session = Depends(get_session), venue_id: int):
    if venue := session.get(Venue, venue_id):
        return venue
    else:
        raise HTTPException(status_code=404, detail="Venue not found")


@router.get("/venues", response_model=list[VenueRead])
def get_films(
    *,
    session: Session = Depends(get_session),
    venue_name: Annotated[str | None, Query(max_length=50)] = None,
):
    if venue_name:
        statement = select(Venue).where(Venue.name == venue_name)
        return session.exec(statement).all() or Response(status_code=204)
    return session.exec(select(Venue)).all() or Response(status_code=204)


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
