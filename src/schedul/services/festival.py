from sqlmodel import Session, select

from models.festival import Festival, FestivalCreate
from models.screening import Screening


def get_festival_db(session: Session, festival_id: int) -> Festival | None:
    return session.get(Festival, festival_id)


def get_festivals_db(session: Session, short_name: str | None = None) -> list[Festival]:
    if short_name:
        statement = select(Festival).where(Festival.short_name == short_name)
        return list(session.exec(statement).all())
    return list(session.exec(select(Festival)).all())


def create_festival_db(session: Session, festival: FestivalCreate) -> Festival:
    db_festival = Festival.model_validate(festival)
    session.add(db_festival)
    session.commit()
    session.refresh(db_festival)
    return db_festival


def delete_festival_db(session: Session, festival_id: int) -> bool:
    if festival := session.get(Festival, festival_id):
        session.delete(festival)
        session.commit()
        return True
    return False


def create_festival_if_required_db(
    session: Session, festival: FestivalCreate
) -> Festival:
    query = session.exec(
        select(Festival).where(Festival.short_name == festival.short_name)
    ).first()
    return query or create_festival_db(session=session, festival=festival)


def get_sessions_db(session: Session, festival_id) -> list[Screening]:
    return list(
        session.exec(
            select(Screening).where(Screening.festival_id == festival_id)
        ).all()
    )
