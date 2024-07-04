from sqlmodel import Session, select

from clients.sql import engine
from models.venue import Venue


def create_venue(name: str) -> Venue:
    with Session(engine) as session:
        db_venue = Venue(name=name)
        session.add(db_venue)
        session.commit()
        session.refresh(db_venue)
        return db_venue


def create_venue_if_required(name: str) -> Venue:
    with Session(engine) as session:
        query = session.exec(select(Venue).where(Venue.name == name)).first()
        return query or create_venue(name=name)


def get_venues_db(session: Session, venue_name: str | None = None):
    if venue_name:
        statement = select(Venue).where(Venue.name == venue_name)
        return list(session.exec(statement).all())
    return list(session.exec(select(Venue)).all())
