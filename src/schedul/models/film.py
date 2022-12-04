from sqlmodel import SQLModel
from sqlmodel import Field  # type: ignore
from typing import Optional

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
