from clients.sql import engine
from models.festival import Festival
from sqlmodel import Session, select


def create_festival(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        db_festival = Festival(full_name=full_name, short_name=short_name)
        session.add(db_festival)
        session.commit()
        session.refresh(db_festival)
        return db_festival


def create_festival_if_required(full_name: str, short_name: str) -> Festival:
    with Session(engine) as session:
        query = session.exec(
            select(Festival).where(Festival.short_name == short_name)
        ).first()
        return query or create_festival(full_name=full_name, short_name=short_name)
