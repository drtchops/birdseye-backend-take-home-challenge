from collections.abc import Sequence
from uuid import UUID

import shortuuid
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Shortlink


class ShortlinkService:
    """Service to handle creation and retrieval of shortlinks"""

    @classmethod
    async def from_slug(cls, slug: str, session: AsyncSession) -> Shortlink | None:
        """Retrieves a shortlink instance from a slug.

        :param slug: The short UUID slug for a shortlink
        :type slug: str
        :param session: An async session connected to a database
        :type session: AsyncSession
        :returns: The retrieved Shortlink instance or None if not found
        :rtype: Shortlink | None
        """
        try:
            uuid = shortuuid.decode(slug)
        except ValueError:
            return None
        return await session.get(Shortlink, uuid)

    @classmethod
    async def create(cls, long_url: str, session: AsyncSession) -> Shortlink:
        """Creates a new shortlink instance for a given URL.

        :param long_url: The long URL to create a shortlink for
        :type long_url: str
        :param session: An async session connected to a database
        :type session: AsyncSession
        :return: The new shortlink instance
        :rtype: Shortlink
        """
        shortlink = Shortlink(long_url=long_url)
        session.add(shortlink)
        await session.commit()
        return shortlink

    @classmethod
    async def get_by_ids(cls, ids: Sequence[UUID], session: AsyncSession) -> dict[UUID, Shortlink]:
        """Returns a mapping of UUID to Shortlink for the requested ids.

        :param ids: A sequence of shortlink UUIDs
        :type ids: Sequence[UUID]
        :param session: An async session connected to a database
        :type session: AsyncSession
        :return: A mapping of UUID to Shortlink
        :rtype: dict[UUID, Shortlink]
        """
        statement = select(Shortlink).where(col(Shortlink.id).in_(ids))
        results = await session.exec(statement)
        return {shortlink.id: shortlink for shortlink in results}
