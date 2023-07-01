import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from clients.sql import get_session
from models.film import Film
from models.user import User
from models.watchlist import Watchlist, WatchlistFilm
from models.watchlist_entry import WatchlistEntry, WatchlistEntryCreate

router = APIRouter(tags=["Users"])


@router.get("/users/{user_uuid}", response_model=User)
def get_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> User:
    if user := session.get(User, user_uuid):
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users", response_model=list[User])
def get_films(
    *,
    session: Session = Depends(get_session),
) -> list[User] | Response:
    return session.exec(select(User)).all() or Response(status_code=204)


@router.post("/users", response_model=User, status_code=201)
def create_user(*, session: Session = Depends(get_session), user: User) -> User:
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_uuid}")
def delete_user(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID
) -> dict[str, bool]:
    if user := session.get(User, user_uuid):
        session.delete(user)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/users/{user_uuid}/watchlist/{film_id}")
def delete_watchlist_entry(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID, film_id: int
) -> dict[str, bool]:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if watchlist_entry := session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == user_uuid)
        .where(WatchlistEntry.film_id == film_id)
    ).first():
        session.delete(watchlist_entry)
        session.commit()
        return {"deleted": True}
    else:
        return {"deleted": False}


@router.post(
    "/users/{user_uuid}/watchlist/{film_id}",
    response_model=WatchlistEntry,
    status_code=201,
)
def create_watchlist_entry(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID, film_id: int
) -> WatchlistEntry:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if not session.get(Film, film_id):
        raise HTTPException(status_code=404, detail="Film not found")

    watchlist_entry = WatchlistEntryCreate(user_uuid=user_uuid, film_id=film_id)
    db_watchlist_entry = WatchlistEntry.from_orm(watchlist_entry)
    session.add(db_watchlist_entry)
    session.commit()
    session.refresh(db_watchlist_entry)
    return db_watchlist_entry


@router.get(
    "/users/{user_uuid}/watchlist",
    response_model=Watchlist,
)
def get_watchlist(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
) -> Watchlist:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

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
