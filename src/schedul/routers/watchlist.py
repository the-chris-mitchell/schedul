import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from clients.sql import get_session
from models.film import Film
from models.user import User
from models.watchlist import Watchlist, WatchlistEntry
from services.watchlist import (
    create_watchlist_entry_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

router = APIRouter(tags=["Users"])


@router.delete("/users/{user_uuid}/watchlist/{film_id}")
def delete_watchlist_entry(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID, film_id: int
) -> dict[str, bool]:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if delete_watchlist_entry_db(session=session, user_uuid=user_uuid, film_id=film_id):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")


@router.put(
    "/users/{user_uuid}/watchlist/{film_id}",
    responses={201: {"model": WatchlistEntry}, 202: {"model": WatchlistEntry}},
)
def create_watchlist_entry(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID, film_id: int
) -> JSONResponse:
    if not session.get(User, user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    if not session.get(Film, film_id):
        raise HTTPException(status_code=404, detail="Film not found")

    if existing_watchlist_entry := session.exec(
        select(WatchlistEntry)
        .where(WatchlistEntry.user_uuid == user_uuid)
        .where(WatchlistEntry.film_id == film_id)
    ).first():
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=jsonable_encoder(existing_watchlist_entry),
        )

    db_watchlist_entry = create_watchlist_entry_db(
        session=session, user_uuid=user_uuid, film_id=film_id
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(db_watchlist_entry),
    )


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

    return get_watchlist_db(session=session, user_uuid=user_uuid)
