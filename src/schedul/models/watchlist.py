import uuid as uuid_pkg
from dataclasses import dataclass
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from models.film import Film
from models.user import User


@dataclass
class WatchlistFilm:
    film: Film
    in_watchlist: bool


class WatchlistEntryBase(SQLModel):
    user_uuid: uuid_pkg.UUID = Field(foreign_key="user.uuid")
    film_id: int = Field(foreign_key="film.id")


class WatchlistEntry(WatchlistEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship()
    film: Film = Relationship()


class WatchlistEntryCreate(WatchlistEntryBase):
    pass


class WatchlistEntryPublic(WatchlistEntryBase):
    id: int
    user: User
    film: Film
