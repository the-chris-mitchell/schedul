from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from clients.sql import get_session
from models.film import Film, FilmCreate, FilmPublic
from services.film import create_film_db, delete_film_db, get_film_db, get_films_db

router = APIRouter(tags=["Films"])


@router.get("/films/{film_id}", response_model=FilmPublic)
def get_film(*, session: Session = Depends(get_session), film_id: int):
    if film := get_film_db(session=session, film_id=film_id):
        return film
    else:
        raise HTTPException(status_code=404, detail="Film not found")


@router.get("/films", response_model=list[FilmPublic])
def get_films(
    *,
    session: Session = Depends(get_session),
    film_name: Annotated[str | None, Query(max_length=50)] = None,
) -> list[Film] | Response:
    return get_films_db(session=session, film_name=film_name) or Response(
        status_code=204
    )


@router.post("/films", response_model=FilmPublic, status_code=201)
def create_film(*, session: Session = Depends(get_session), film: FilmCreate):
    return create_film_db(session=session, film=film)


@router.delete("/films/{film_id}")
def delete_film(*, session: Session = Depends(get_session), film_id: int):
    if delete_film_db(session=session, film_id=film_id):
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Film not found")
