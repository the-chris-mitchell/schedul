import uuid as uuid_pkg
from dataclasses import dataclass
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from schedul.models.screening import Screening, ScreeningPublic
from schedul.models.user import User


@dataclass
class BookingScreening:
    screening: ScreeningPublic
    is_booked: bool


class BookingBase(SQLModel):
    user_uuid: uuid_pkg.UUID = Field(foreign_key="user.uuid")
    screening_id: int = Field(foreign_key="screening.id")


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship()
    screening: Screening = Relationship()


class BookingCreate(BookingBase):
    pass


class BookingPublic(BookingBase):
    id: int
    user: User
    screening: Screening
