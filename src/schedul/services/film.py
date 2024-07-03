from sqlmodel import Session, select

from clients.sql import engine
from models.film import Film


def create_film(name: str, runtime: int) -> Film:
    with Session(engine) as session:
        db_film = Film(name=name, runtime=runtime)
        session.add(db_film)
        session.commit()
        session.refresh(db_film)
        return db_film


def create_film_if_required(name: str, runtime: int) -> Film:
    with Session(engine) as session:
        query = session.exec(select(Film).where(Film.name == name)).first()
        return query or create_film(name=name, runtime=runtime)


def get_films_db(session: Session, film_name: str | None = None):
    if film_name:
        statement = select(Film).where(Film.name == film_name)
        return list(session.exec(statement).all())
    return list(session.exec(select(Film)).all())
