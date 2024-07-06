from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from clients.sql import get_session
from models.venue import Venue, VenueCreate, VenuePublic
from services.venue import get_venues_db

router = APIRouter(tags=["Venues"])


@router.get("/venues/{venue_id}", response_model=VenuePublic)
def get_venue(*, session: Session = Depends(get_session), venue_id: int):
    if venue := session.get(Venue, venue_id):
        return venue
    else:
        raise HTTPException(status_code=404, detail="Venue not found")


@router.get("/venues", response_model=list[VenuePublic])
def get_venues(
    *,
    session: Session = Depends(get_session),
    venue_name: Annotated[str | None, Query(max_length=50)] = None,
):
    return get_venues_db(session=session, venue_name=venue_name) or Response(
        status_code=204
    )


@router.post("/venues", response_model=VenuePublic, status_code=201)
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
