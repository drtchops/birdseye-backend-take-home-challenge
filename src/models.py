import uuid

from sqlmodel import Field, SQLModel


class Shortlink(SQLModel, table=True):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)
    url: str
