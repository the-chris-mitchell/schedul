import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from clients.sql import get_session
from models.festival import Festival
from models.user import User
from models.watchlist_entry import (
    WatchlistEntry,
    WatchlistEntryCreate,
    WatchlistEntryCreateRequest,
    WatchlistEntryRead,
)

router = APIRouter(tags=["Users"])


@router.get("/users/{user_uuid}", response_model=User)
def get_user(*, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID):
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
def create_user(*, session: Session = Depends(get_session), user: User):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_uuid}")
def delete_user(*, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID):
    if user := session.get(User, user_uuid):
        session.delete(user)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/users/{user_uuid}/festivals/{festival_id}",
    response_model=WatchlistEntry,
    status_code=201,
)
def create_watchlist_entry(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
    festival_id: int,
    request: WatchlistEntryCreateRequest,
):
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")
    if not session.get(Festival, festival_id):
        raise HTTPException(status_code=404, detail="Festival not found")

    watchlist_entry = WatchlistEntryCreate(
        user_uuid=user_uuid, film_id=request.film_id, festival_id=festival_id
    )
    db_watchlist_entry = WatchlistEntry.from_orm(watchlist_entry)
    session.add(db_watchlist_entry)
    session.commit()
    session.refresh(db_watchlist_entry)
    return db_watchlist_entry


@router.get(
    "/users/{user_uuid}/festivals/{festival_id}",
    response_model=list[WatchlistEntryRead],
)
def get_watchlist(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
    festival_id: int,
):
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")
    if not session.get(Festival, festival_id):
        raise HTTPException(status_code=404, detail="Festival not found")

    return session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == user_uuid)
        .where(WatchlistEntry.festival_id == festival_id)
    ).all()
