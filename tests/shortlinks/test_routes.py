import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_create_shortlink(client: AsyncClient) -> None:
    """Tests that creating a valid shortlink works as expected"""
    long_url = "http://example.com/long-url"
    response = await client.post("/shorten", json={"long_url": long_url})
    data = response.json()

    assert response.status_code == 201
    assert data
    slug = data.get("slug")
    assert slug
    assert data.get("short_url") == f"http://test/{slug}"


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
