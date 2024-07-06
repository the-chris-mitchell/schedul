from sqlmodel import Session, select

from models.venue import Venue, VenueCreate


def get_venue_db(session: Session, venue_id: int) -> Venue | None:
    return session.get(Venue, venue_id)


def get_venues_db(session: Session, venue_name: str | None = None):
    if venue_name:
        statement = select(Venue).where(Venue.name == venue_name)
        return list(session.exec(statement).all())
    return list(session.exec(select(Venue)).all())


def create_venue_db(session: Session, venue: VenueCreate) -> Venue:
    db_venue = Venue.model_validate(venue)
    session.add(db_venue)
    session.commit()
    session.refresh(db_venue)
    return db_venue


def delete_venue_db(session: Session, venue_id: int) -> bool:
    if venue := session.get(Venue, venue_id):
        session.delete(venue)
        session.commit()
        return True
    return False


def create_venue_if_required(session: Session, venue: VenueCreate) -> Venue:
    query = session.exec(select(Venue).where(Venue.name == venue.name)).first()
    return query or create_venue_db(session=session, venue=venue)
