from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session

from .service import ShortlinkService


class ShortlinkCreate(BaseModel):
    """The input for creating a new shortlink"""

    long_url: HttpUrl
    """The long URL to point the new shortlink to"""


class ShortlinkResponse(BaseModel):
    """A response detailing a newly created shortlink"""

    slug: str
    """The slug used to identify the shortlink"""

    short_url: str
    """THe URL the shortlink can be accessed at"""


router = APIRouter()


@router.post("/shorten", status_code=status.HTTP_201_CREATED, response_model=ShortlinkResponse, name="Shorten URL")
async def post_shorten(
    shortlink_create: ShortlinkCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShortlinkResponse:
    """Create a new shortlink with the given long URL and return it"""
    shortlink = await ShortlinkService.create(str(shortlink_create.long_url), session)
    return ShortlinkResponse(slug=shortlink.slug, short_url=shortlink.short_url)


@router.get("/{slug}", status_code=status.HTTP_307_TEMPORARY_REDIRECT, response_model=None, name="Access Shortlink")
async def get_slug(
    slug: str,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RedirectResponse | dict[str, str]:
    """Redirect using the given shortlink, or return a 404 if none is found"""
    shortlink = await ShortlinkService.from_slug(slug, session)
    if shortlink:
        return RedirectResponse(shortlink.long_url)
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"detail": "Not Found"}
