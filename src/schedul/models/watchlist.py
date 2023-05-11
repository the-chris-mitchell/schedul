import uuid as uuid_pkg
from dataclasses import dataclass
from typing import Optional

from models.festival import Festival
from models.film import Film
from models.user import User
from models.venue import Venue
from sqlmodel import Field, Relationship, SQLModel


class WatchlistEntryBase(SQLModel):
    user_uuid: uuid_pkg.UUID = Field(foreign_key="user.uuid")
    film_id: int = Field(foreign_key="film.id")
    festival_id: int = Field(foreign_key="festival.id")


class WatchlistEntry(WatchlistEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship()
    film: Film = Relationship()
    festival: Festival = Relationship()


class WatchlistEntryCreate(WatchlistEntryBase):
    pass


class WatchlistEntryRead(WatchlistEntryBase):
    id: int
    user: User
    film: Film
    festival: Festival


@dataclass
class WatchlistEntryCreateRequest:
    film_id: int
