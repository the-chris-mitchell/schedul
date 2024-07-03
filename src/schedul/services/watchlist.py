import uuid as uuid_pkg

from sqlmodel import Session, select

from models.film import Film
from models.watchlist import (
    Watchlist,
    WatchlistEntry,
    WatchlistEntryCreate,
    WatchlistFilm,
)


def get_watchlist_db(session: Session, user_uuid: uuid_pkg.UUID) -> Watchlist:
    watchlist_entries = session.exec(
        select(WatchlistEntry).where(WatchlistEntry.user_uuid == user_uuid)
    ).all()

    films = session.exec(select(Film)).all()

    watchlist_films = []

    for film in films:
        watchlist_entry_ids = [entry.film_id for entry in watchlist_entries]
        if film.id in watchlist_entry_ids:
            watchlist_films.append(WatchlistFilm(film, True))
        else:
            watchlist_films.append(WatchlistFilm(film, False))

    return Watchlist(watchlist_films)


def create_watchlist_entry_db(
    session: Session, user_uuid: uuid_pkg.UUID, film_id: int
) -> WatchlistEntry:
    watchlist_entry = WatchlistEntryCreate(user_uuid=user_uuid, film_id=film_id)
    db_watchlist_entry = WatchlistEntry.from_orm(watchlist_entry)
    session.add(db_watchlist_entry)
    session.commit()
    session.refresh(db_watchlist_entry)
    return db_watchlist_entry


def delete_watchlist_entry_db(session: Session, user_uuid: uuid_pkg.UUID, film_id: int):
    if watchlist_entries := session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == user_uuid)
        .where(WatchlistEntry.film_id == film_id)
    ).all():
        for watchlist_entry in watchlist_entries:
            session.delete(watchlist_entry)
            session.commit()
            return True
