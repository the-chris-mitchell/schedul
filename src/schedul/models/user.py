import uuid as uuid_pkg

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    uuid: uuid_pkg.UUID = Field(primary_key=True)
