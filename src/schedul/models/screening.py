from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.festival import Festival
from models.film import Film
from models.venue import Venue
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class ScreeningBase(SQLModel):
    start_time: datetime
    end_time: datetime
    link: str
    film_id: int = Field(foreign_key="film.id")
    venue_id: int = Field(foreign_key="venue.id")
    festival_id: int = Field(foreign_key="festival.id")


class Screening(ScreeningBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film: Film = Relationship()
    venue: Venue = Relationship()
    festival: Festival = Relationship()


class ScreeningCreate(ScreeningBase):
    pass


class ScreeningRead(ScreeningBase):
    id: int
    film: Film
    venue: Venue


@dataclass
class ScoredScreening:
    screening: Screening
    score: int = 0
