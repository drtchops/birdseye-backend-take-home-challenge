import uuid
from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel


class ShortlinkStat(SQLModel, table=True):
    """A model containing visitation stats for a shortlink"""

    shortlink_id: uuid.UUID = Field(primary_key=True, foreign_key="shortlink.id")
    """The id of the shortlink, used as the primary key for this table"""

    visits: int = Field(default=0, index=True)
    """The total visit count for this shortlink"""

    last_visit: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))
    """The timestamp for the last time this shortlink was visited"""
