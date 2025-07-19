from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from shortlinks.service import ShortlinkService
from stats.service import ShortlinkWithStats

from .service import StatMetric, StatsService

router = APIRouter()


@router.get("/stats", name="Top Stats")
async def get_stats(
    *,
    metric: Annotated[StatMetric, Query(description="Which metric to sort the results by")] = StatMetric.VISITS,
    limit: Annotated[int, Query(description="How many results to return", ge=0, le=100)] = 10,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ShortlinkWithStats]:
    """Gets the top shortlink stats based on the requested metric and limit"""
    return await StatsService.get_top_stats(metric, limit, session)


@router.get("/stats/{slug}", name="Stats for Shortlink", response_model=ShortlinkWithStats)
async def get_stats_for_slug(
    slug: Annotated[str, Path(description="The slug used to identify the shortlink")],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str] | ShortlinkWithStats:
    """Gets the stats for a specific shortlink"""
    shortlink = await ShortlinkService.from_slug(slug, session)
    if not shortlink:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": "Not Found"}
    return await StatsService.get_shortlink_stats(shortlink, session)
