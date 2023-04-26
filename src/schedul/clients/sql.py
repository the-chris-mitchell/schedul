import os

from sqlmodel import Session, SQLModel, create_engine

if db_url := os.getenv("DATABASE_URL"):
    engine = create_engine(db_url)
else:
    engine = create_engine("sqlite:///db.sqlite")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
