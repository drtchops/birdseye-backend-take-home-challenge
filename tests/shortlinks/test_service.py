from uuid import uuid4

import pytest
import shortuuid
from sqlmodel.ext.asyncio.session import AsyncSession

from shortlinks.models import Shortlink
from shortlinks.service import ShortlinkService

pytestmark = pytest.mark.anyio


async def test_loading_shortlink(session: AsyncSession, shortlink: Shortlink) -> None:
    """Tests loading an existing shortlink by slug"""
    loaded_shortlink = await ShortlinkService.from_slug(shortlink.slug, session)
    assert loaded_shortlink
    assert loaded_shortlink == shortlink


async def test_loading_shortlink_does_not_exist(session: AsyncSession) -> None:
    """Tests loading a shortlink by slug that does not exist returns None"""
    slug = shortuuid.encode(uuid4())
    loaded_shortlink = await ShortlinkService.from_slug(slug, session)
    assert not loaded_shortlink


async def test_loading_invalid_shortlink(session: AsyncSession) -> None:
    """Tests loading a shortlink for an invalid UUID returns None"""
    loaded_shortlink = await ShortlinkService.from_slug("invalid", session)
    assert not loaded_shortlink


async def test_create_shortlink(session: AsyncSession) -> None:
    """Tests creating a new shortlink from a long URL"""
    long_url = "https://www.example.com/very/long/url"
    new_shortlink = await ShortlinkService.create(long_url, session)
    assert new_shortlink.id
    assert new_shortlink.long_url == long_url


async def test_create_duplicate_shortlink(session: AsyncSession, shortlink: Shortlink) -> None:
    """Tests creating a new shortlink with a long URL that already has an existing shortlink"""
    new_shortlink = await ShortlinkService.create(shortlink.long_url, session)
    assert new_shortlink.id != shortlink.id
    assert new_shortlink.long_url == shortlink.long_url


async def test_get_by_ids(session: AsyncSession) -> None:
    """Tests getting multiple shortlinks by UUID"""
    shortlinks: list[Shortlink] = []
    for i in range(3):
        shortlink = Shortlink(long_url=f"https://www.example.com/very/long/url/{i}")
        session.add(shortlink)
        shortlinks.append(shortlink)
    await session.commit()

    ids = [sl.id for sl in shortlinks]
    new_uuid = uuid4()
    ids.append(new_uuid)
    loaded_shortlinks = await ShortlinkService.get_by_ids(ids, session)
    assert len(loaded_shortlinks) == 3
    for shortlink in shortlinks:
        assert loaded_shortlinks[shortlink.id] == shortlink
    assert new_uuid not in loaded_shortlinks
