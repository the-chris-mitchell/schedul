from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlmodel import select
from clients.sql import get_session

from models.film import FilmCreate, FilmRead, Film


router = APIRouter(tags=["Films"])


@router.get("/films/{film_id}", response_model=FilmRead)
def get_film(*, session: Session = Depends(get_session), film_id: int):
    if film := session.get(Film, film_id):
        return film
    else:
        raise HTTPException(status_code=404, detail="Film not found")


@router.get("/films", response_model=list[FilmRead])
def get_films(*, session: Session = Depends(get_session)):
    return session.exec(select(Film)).all()


@router.post("/films", response_model=FilmRead, status_code=201)
def create_film(*, session: Session = Depends(get_session), film: FilmCreate):
    db_film = Film.from_orm(film)
    session.add(db_film)
    session.commit()
    session.refresh(db_film)
    return db_film


@router.delete("/films/{film_id}")
def delete_film(*, session: Session = Depends(get_session), film_id: int):
    if film := session.get(Film, film_id):
        session.delete(film)
        session.commit()
        return {"deleted": True}
    else:
        raise HTTPException(status_code=404, detail="Film not found")
