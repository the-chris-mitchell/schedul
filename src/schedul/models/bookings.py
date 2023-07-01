import uuid as uuid_pkg
from dataclasses import dataclass
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from models.film import Film
from models.screening import Screening
from models.user import User
from models.venue import Venue


@dataclass
class BookingScreening:
    screening: Screening
    film: Film
    venue: Venue
    is_booked: bool


@dataclass
class Bookings:
    screenings: list[BookingScreening]


class BookingBase(SQLModel):
    user_uuid: uuid_pkg.UUID = Field(foreign_key="user.uuid")
    screening_id: int = Field(foreign_key="screening.id")


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship()
    screening: Screening = Relationship()


class BookingCreate(BookingBase):
    pass


class BookingRead(BookingBase):
    id: int
    user: User
    screening: Screening
