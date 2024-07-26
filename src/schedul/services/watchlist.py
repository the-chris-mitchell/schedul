import uuid as uuid_pkg

from fastapi import HTTPException
from sqlmodel import Session, select

from schedul.models.film import Film
from schedul.models.watchlist import WatchlistEntry, WatchlistEntryCreate, WatchlistFilm
from schedul.services.film import get_film_db
from schedul.services.users import get_user_db


def get_watchlist_entries_db(
    session: Session, user_uuid: uuid_pkg.UUID
) -> list[WatchlistEntry]:
    return list(
        session.exec(
            select(WatchlistEntry).where(WatchlistEntry.user_uuid == user_uuid)
        ).all()
    )


def get_watchlist_db(session: Session, user_uuid: uuid_pkg.UUID) -> list[WatchlistFilm]:
    watchlist_entries = get_watchlist_entries_db(session=session, user_uuid=user_uuid)

    films = session.exec(select(Film)).all()

    watchlist_films = []

    for film in films:
        watchlist_entry_ids = [entry.film_id for entry in watchlist_entries]
        if film.id in watchlist_entry_ids:
            watchlist_films.append(WatchlistFilm(film, True))
        else:
            watchlist_films.append(WatchlistFilm(film, False))

    return watchlist_films


def create_watchlist_entry_db(
    session: Session, watchlist_entry: WatchlistEntryCreate
) -> WatchlistEntry:
    db_watchlist_entry = WatchlistEntry.model_validate(watchlist_entry)
    session.add(db_watchlist_entry)
    session.commit()
    session.refresh(db_watchlist_entry)
    return db_watchlist_entry


def create_watchlist_entry_if_required_db(
    session: Session, watchlist_entry: WatchlistEntryCreate
) -> tuple[WatchlistEntry, bool]:
    if not get_user_db(session=session, user_uuid=watchlist_entry.user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if not get_film_db(session=session, film_id=watchlist_entry.film_id):
        raise HTTPException(status_code=404, detail="Film not found")
    if response := session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == watchlist_entry.user_uuid)
        .where(WatchlistEntry.film_id == watchlist_entry.film_id)
    ).first():
        return (response, False)
    else:
        return (
            create_watchlist_entry_db(session=session, watchlist_entry=watchlist_entry),
            True,
        )


def delete_watchlist_entry_db(
    session: Session, user_uuid: uuid_pkg.UUID, film_id: int
) -> bool:
    if watchlist_entries := session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == user_uuid)
        .where(WatchlistEntry.film_id == film_id)
    ).all():
        for watchlist_entry in watchlist_entries:
            session.delete(watchlist_entry)
            session.commit()
        return True
    return False
