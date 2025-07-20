from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from shortlinks.models import Shortlink
from stats.models import ShortlinkStat


@pytest.fixture()
async def shortlink_with_stats(session: AsyncSession, shortlink: Shortlink) -> Shortlink:
    stats = ShortlinkStat(
        shortlink_id=shortlink.id,
        visits=10,
        last_visit=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
    )
    session.add(stats)
    await session.commit()
    return shortlink


@pytest.fixture()
async def shortlink_list_with_stats(session: AsyncSession, shortlink_list: list[Shortlink]) -> list[Shortlink]:
    start_dt = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    for i, shortlink in enumerate(shortlink_list):
        stats = ShortlinkStat(
            shortlink_id=shortlink.id,
            visits=i,
            last_visit=start_dt - timedelta(hours=i),
        )
        session.add(stats)
    await session.commit()
    return shortlink_list
