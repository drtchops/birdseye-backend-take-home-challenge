from datetime import UTC, datetime

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from shortlinks.models import Shortlink
from stats.models import ShortlinkStat
from stats.service import StatsService

pytestmark = pytest.mark.anyio


async def test_record_first_visit(session: AsyncSession, shortlink: Shortlink) -> None:
    """Tests recording a visit for a shortlink that has not yet had visits"""
    last_visit = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    await StatsService.record_visit(shortlink.id, last_visit, session)

    stats = await session.get(ShortlinkStat, shortlink.id)
    assert stats
    assert stats.visits == 1
    assert stats.last_visit == last_visit


async def test_record_subsequent_visit(session: AsyncSession, shortlink_with_stats: Shortlink) -> None:
    """Tests recording a visit for a shortlink that has already had visits"""
    last_visit = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    await StatsService.record_visit(shortlink_with_stats.id, last_visit, session)

    stats = await session.get(ShortlinkStat, shortlink_with_stats.id)
    assert stats
    assert stats.visits == 11
    assert stats.last_visit != last_visit
