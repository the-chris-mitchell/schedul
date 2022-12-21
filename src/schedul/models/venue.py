from typing import Optional

from sqlmodel import Field, SQLModel


class VenueBase(SQLModel):
    name: str


class Venue(VenueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class VenueCreate(VenueBase):
    pass


class VenueRead(VenueBase):
    id: int
