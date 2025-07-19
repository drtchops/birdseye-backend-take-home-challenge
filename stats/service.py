from datetime import datetime
from enum import StrEnum
from typing import Annotated, Self
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlmodel import col, select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from shortlinks.models import Shortlink
from shortlinks.service import ShortlinkService

from .models import ShortlinkStat


class ShortlinkWithStats(BaseModel):
    """A response detailing a shortlink and its stats"""

    slug: str = Field(description="The slug used to identify the shortlink")
    short_url: str = Field(description="The URL the shortlink can be accessed at")
    long_url: str = Field(description="The URL the shortlink redirects to")
    visits: int = Field(description="The number of visits to this shortlink")
    last_visit: datetime | None = Field(description="The timestamp of the last visit to this shortlink")

    @classmethod
    def from_models(cls, shortlink: Shortlink | None = None, stats: ShortlinkStat | None = None) -> Self:
        """Creates a new instance from a shortlink and/or shortlink stats"""
        return cls(
            slug=shortlink.slug if shortlink else "",
            short_url=shortlink.short_url if shortlink else "",
            long_url=shortlink.long_url if shortlink else "",
            visits=stats.visits if stats else 0,
            last_visit=stats.last_visit if stats else None,
        )


class StatMetric(StrEnum):
    """Enum defining what metric options can be selected for sorting stats"""

    VISITS = "visits"
    LAST_VISIT = "last_visit"


class StatsService:
    """Service to handle tracking and querying stats on shortlinks"""

    @classmethod
    async def record_visit(
        cls,
        shortlink_id: UUID,
        last_visit: datetime,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        """Records a visit to a shortlink by incrementing its visit count
        and updating the last visit timestamp if applicable.

        :param shortlink_id: The UUID of the shortlink to update
        :type shortlink_id: str
        :param last_visit: The timestamp of the visit that's being recorded
        :type last_visit: datetime
        :param session: An async session connected to a database
        :type session: AsyncSession
        """
        # One disadvantage with SQLModel is it's not as nice to do raw optimized SQL like this
        await session.execute(  # pyright: ignore[reportDeprecated]
            text("""
                INSERT INTO shortlinkstat AS sls
                    (shortlink_id, visits, last_visit)
                VALUES (:shortlink_id, 1, :last_visit)
                ON CONFLICT (shortlink_id)
                DO UPDATE SET
                    visits = sls.visits + 1,
                    last_visit = (CASE
                        WHEN sls.last_visit < EXCLUDED.last_visit THEN EXCLUDED.last_visit
                        ELSE sls.last_visit
                    END)
            """),
            {
                "shortlink_id": shortlink_id,
                "last_visit": last_visit,
            },
        )
        await session.commit()

    @classmethod
    async def get_top_stats(
        cls,
        metric: StatMetric,
        limit: int,
        session: AsyncSession,
    ) -> list[ShortlinkWithStats]:
        """Returns a list of the top shortlinks by the specified metric.

        :param metric: The metric to sort by
        :type metric: StatMetric
        :param limit: The total number of shortlinks to return
        :type limit: int
        :param session: An async session connected to a database
        :type session: AsyncSession
        :return: A list of the top shortlinks with stats
        :rtype: ShortlinkWithStats
        """
        column = ShortlinkStat.visits if metric == StatMetric.VISITS else ShortlinkStat.last_visit
        statement = select(ShortlinkStat).order_by(col(column).desc()).limit(limit)
        results = list(await session.exec(statement))
        ids = [stat.shortlink_id for stat in results]
        shortlinks_by_id = await ShortlinkService.get_by_ids(ids, session)
        stats: list[ShortlinkWithStats] = []
        for stat in results:
            shortlink = shortlinks_by_id.get(stat.shortlink_id)
            stats.append(ShortlinkWithStats.from_models(shortlink, stat))
        return stats

    @classmethod
    async def get_shortlink_stats(cls, shortlink: Shortlink, session: AsyncSession) -> ShortlinkWithStats:
        """Gets the stats for a particular shortlink.

        :param shortlink: The shortlink to retrieve metrics for
        :type shortlink: Shortlink
        :param session: An async session connected to a database
        :type session: AsyncSession
        :return: The shortlink with its stats
        :rtype: ShortlinkWithStats
        """
        stats = await session.get(ShortlinkStat, shortlink.id)
        return ShortlinkWithStats.from_models(shortlink, stats)
