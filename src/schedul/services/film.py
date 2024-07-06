from sqlmodel import Session, select

from models.film import Film, FilmCreate


def create_film_db(session: Session, film: FilmCreate) -> Film:
    db_film = Film.model_validate(film)
    session.add(db_film)
    session.commit()
    session.refresh(db_film)
    return db_film


def delete_film_db(session: Session, film_id: int) -> bool:
    if film := session.get(Film, film_id):
        session.delete(film)
        session.commit()
        return True
    return False


def create_film_if_required_db(session: Session, film: FilmCreate) -> Film:
    query = session.exec(select(Film).where(Film.name == film.name)).first()
    return query or create_film_db(session=session, film=film)


def get_film_db(session: Session, film_id: int) -> Film | None:
    return session.get(Film, film_id)


def get_films_db(session: Session, film_name: str | None = None):
    if film_name:
        statement = select(Film).where(Film.name == film_name)
        return list(session.exec(statement).all())
    return list(session.exec(select(Film)).all())
