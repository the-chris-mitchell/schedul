import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session

from clients.sql import get_session
from models.watchlist import WatchlistEntry, WatchlistEntryCreate, WatchlistFilm
from services.users import get_user_db
from services.watchlist import (
    create_watchlist_entry_if_required_db,
    delete_watchlist_entry_db,
    get_watchlist_db,
)

router = APIRouter(tags=["Users"])


@router.delete("/users/{user_uuid}/watchlist/{film_id}")
def delete_watchlist_entry(
    *, session: Session = Depends(get_session), user_uuid: uuid_pkg.UUID, film_id: int
) -> dict[str, bool]:
    if not get_user_db(session=session, user_uuid=user_uuid):
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
    watchlist_entry, created = create_watchlist_entry_if_required_db(
        session=session,
        watchlist_entry=WatchlistEntryCreate(user_uuid=user_uuid, film_id=film_id),
    )
    if created:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(watchlist_entry),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=jsonable_encoder(watchlist_entry),
        )


@router.get(
    "/users/{user_uuid}/watchlist",
    response_model=list[WatchlistFilm],
)
def get_watchlist(
    *,
    session: Session = Depends(get_session),
    user_uuid: uuid_pkg.UUID,
) -> list[WatchlistFilm]:
    if not get_user_db(session=session, user_uuid=user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    return get_watchlist_db(session=session, user_uuid=user_uuid)
