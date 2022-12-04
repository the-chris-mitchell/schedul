from sqlmodel import SQLModel
from sqlmodel import Field  # type: ignore
from typing import Optional


class VenueBase(SQLModel):
    name: str

class Venue(VenueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class VenueCreate(VenueBase):
    pass

class VenueRead(VenueBase):
    id: int
