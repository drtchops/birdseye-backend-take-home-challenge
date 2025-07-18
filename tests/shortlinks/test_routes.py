import pytest
import shortuuid
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from shortlinks.models import Shortlink

pytestmark = pytest.mark.anyio


async def test_create_shortlink(session: AsyncSession, client: AsyncClient) -> None:
    """Tests that creating a valid shortlink works as expected"""
    long_url = "http://example.com/long-url"
    response = await client.post("/shorten", json={"long_url": long_url})
    data = response.json()

    assert response.status_code == 201
    assert data
    slug = data.get("slug", "")
    assert slug
    assert "short_url" in data
    shortlink_id = shortuuid.decode(slug)
    shortlink = await session.get(Shortlink, shortlink_id)
    assert shortlink


async def test_create_shortlink_missing_url(client: AsyncClient) -> None:
    """Tests that creating a shortlink without a url returns an error"""
    response = await client.post("/shorten")
    data = response.json()

    assert response.status_code == 422
    assert data


async def test_create_shortlink_invalid_url(client: AsyncClient) -> None:
    """Tests that creating a shortlink with an invalid url returns an error"""
    long_url = "bad url"
    response = await client.post("/shorten", json={"long_url": long_url})
    data = response.json()

    assert response.status_code == 422
    assert data


@pytest.mark.parametrize(
    ("protocol", "is_valid"),
    (
        ("http", True),
        ("https", True),
        ("wss", False),
        ("steam", False),
    ),
)
async def test_create_shortlink_protocol(client: AsyncClient, protocol: str, is_valid: bool) -> None:
    """Tests that creating a shortlink only works with http or https"""
    long_url = f"{protocol}://example.com/long-url"
    response = await client.post("/shorten", json={"long_url": long_url})
    data = response.json()

    assert data
    expected_code = 201 if is_valid else 422
    assert response.status_code == expected_code


async def test_create_duplicate_link(session: AsyncSession, client: AsyncClient) -> None:
    """Tests that creating multiple shortlinks with the same long url
    results in multiple different shortlink instances"""
    long_url = "http://example.com/long-url"

    response1 = await client.post("/shorten", json={"long_url": long_url})
    data1 = response1.json()
    assert response1.status_code == 201
    assert data1
    slug1 = data1.get("slug", "")
    assert slug1
    assert "short_url" in data1
    shortlink_id1 = shortuuid.decode(slug1)
    shortlink1 = await session.get(Shortlink, shortlink_id1)
    assert shortlink1

    response2 = await client.post("/shorten", json={"long_url": long_url})
    data2 = response2.json()
    assert response2.status_code == 201
    assert data2
    slug2 = data2.get("slug", "")
    assert slug2
    assert "short_url" in data2
    shortlink_id2 = shortuuid.decode(slug2)
    shortlink2 = await session.get(Shortlink, shortlink_id2)
    assert shortlink2

    assert slug1 != slug2
    assert shortlink1 != shortlink2
    assert shortlink1.long_url == shortlink2.long_url
