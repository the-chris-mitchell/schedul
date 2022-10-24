
from sqlmodel import Relationship, SQLModel

from models.session_sql import SessionSQL


class FestivalSQL(SQLModel):      
    full_name: str
    short_name: str
    # sessions: list["SessionSQL"] = Relationship(back_populates="team")