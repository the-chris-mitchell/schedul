from typing import Optional

from sqlmodel import Field, SQLModel


class VenueBase(SQLModel):
    name: str

    def __hash__(self):
        return hash(str(self))


class Venue(VenueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class VenueCreate(VenueBase):
    pass


class VenueRead(VenueBase):
    id: int
