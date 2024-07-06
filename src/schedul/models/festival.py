from typing import Optional

from sqlmodel import Field, SQLModel


class FestivalBase(SQLModel):
    full_name: str
    short_name: str


class Festival(FestivalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FestivalCreate(FestivalBase):
    pass


class FestivalPublic(FestivalBase):
    id: int
