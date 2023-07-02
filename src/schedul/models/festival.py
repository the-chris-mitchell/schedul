from typing import Optional

from sqlmodel import Field, SQLModel


class FestivalBase(SQLModel):
    full_name: str
    short_name: str


class Festival(FestivalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FestivalCreate(FestivalBase):
    pass


class FestivalRead(FestivalBase):
    id: int


class FestivalUpdate(FestivalBase):
    full_name: Optional[str] = None  # type: ignore
    short_name: Optional[str] = None  # type: ignore
