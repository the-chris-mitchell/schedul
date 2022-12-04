import datetime
from sqlmodel import SQLModel
from sqlmodel import Field  # type: ignore
from typing import Optional

class FestivalBase(SQLModel):
    full_name: str
    short_name: str
    max_sessions: Optional[int] = 1
    buffer_time: Optional[int] = 20
    excluded_dates: Optional[list[datetime.date]]

class Festival(FestivalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class FestivalCreate(FestivalBase):
    pass

class FestivalRead(FestivalBase):
    id: int

class FestivalUpdate(FestivalBase):
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    max_sessions: Optional[int] = None
    buffer_time: Optional[int] = None
    excluded_dates: Optional[list[datetime.date]] = None