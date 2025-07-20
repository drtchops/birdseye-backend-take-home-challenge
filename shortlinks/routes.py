from datetime import UTC, datetime
from typing import Annotated, Self

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, HttpUrl
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from stats.service import StatsService

from .models import Shortlink as ShortlinkModel
from .service import ShortlinkService


class ShortlinkCreate(BaseModel):
    """The input for creating a new shortlink"""

    long_url: HttpUrl = Field(description="The long URL to point the new shortlink to")


class Shortlink(BaseModel):
    """A response detailing a newly created shortlink"""

    slug: str = Field(description="The slug used to identify the shortlink")
    short_url: str = Field(description="The URL the shortlink can be accessed at")
    long_url: str = Field(description="The URL the shortlink redirects to")

    @classmethod
    def from_model(cls, shortlink: ShortlinkModel) -> Self:
        """Creates a new instance from a shortlink model"""
        return cls(
            slug=shortlink.slug,
            short_url=shortlink.short_url,
            long_url=shortlink.long_url,
        )


router = APIRouter()


@router.post("/shorten", status_code=status.HTTP_201_CREATED, response_model=Shortlink, name="Shorten URL")
async def post_shorten(
    shortlink_create: ShortlinkCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Shortlink:
    """Create a new shortlink with the given long URL and return it"""
    shortlink = await ShortlinkService.create(str(shortlink_create.long_url), session)
    return Shortlink.from_model(shortlink)


@router.get("/{slug}", status_code=status.HTTP_307_TEMPORARY_REDIRECT, response_model=None, name="Access Shortlink")
async def get_slug(
    slug: Annotated[str, Path(description="The slug used to identify the shortlink")],
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    """Redirect using the given shortlink, or return a 404 if none is found"""
    shortlink = await ShortlinkService.from_slug(slug, session)
    if not shortlink:
        return JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)

    background_tasks.add_task(StatsService.record_visit, shortlink.id, datetime.now(UTC), session)
    return RedirectResponse(shortlink.long_url)
