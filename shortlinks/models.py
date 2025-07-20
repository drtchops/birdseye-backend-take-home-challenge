import uuid
from datetime import UTC, datetime
from functools import cached_property

import shortuuid
from sqlmodel import Column, DateTime, Field, SQLModel

from core.config import get_settings


class Shortlink(SQLModel, table=True):
    """A model containing a mapping of UUID to long URL, also known as shortlinks"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    """The UUID of a shortlink"""

    long_url: str
    """The long URL that a shortlink redirects to"""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    """When the shortlink was created"""

    @cached_property
    def slug(self) -> str:
        """The URL-friendly shortened form of the shortlink's UUID"""
        return shortuuid.encode(self.id)

    @cached_property
    def short_url(self) -> str:
        """The URL to the service where this shortlink is hosted"""
        settings = get_settings()
        return f"{settings.service_root}/{self.slug}"
