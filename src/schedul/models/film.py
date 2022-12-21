from typing import Optional

from sqlmodel import Field, SQLModel


class FilmBase(SQLModel):
    name: str
    runtime: int
    year: int


class Film(FilmBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FilmCreate(FilmBase):
    pass


class FilmRead(FilmBase):
    id: int
