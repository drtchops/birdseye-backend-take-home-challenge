from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import shortuuid
from httpx import AsyncClient

from shortlinks.models import Shortlink

pytestmark = pytest.mark.anyio


@pytest.mark.usefixtures("shortlink_list_with_stats")
async def test_top_stats(client: AsyncClient) -> None:
    """Tests that the top 10 shortlinks by visits is returned by default"""
    response = await client.get("/stats")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 10
    assert [d["visits"] for d in data] == list(reversed(range(90, 100)))


@pytest.mark.usefixtures("shortlink_list_with_stats")
async def test_top_stats_by_last_visit(client: AsyncClient) -> None:
    """Tests sorting the top stats by last visit"""
    start_dt = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    params = {"metric": "last_visit"}
    response = await client.get("/stats", params=params)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 10
    assert [datetime.fromisoformat(d["last_visit"]).replace(tzinfo=UTC) for d in data] == [
        start_dt - timedelta(hours=i) for i in range(10)
    ]


@pytest.mark.usefixtures("shortlink_list_with_stats")
async def test_top_stats_with_limit(client: AsyncClient) -> None:
    """Tests getting more than the default limit for top stats"""
    params = {"limit": 25}
    response = await client.get("/stats", params=params)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 25
    assert [d["visits"] for d in data] == list(reversed(range(75, 100)))


@pytest.mark.usefixtures("shortlink_list_with_stats")
async def test_top_stats_with_metric_and_limit(client: AsyncClient) -> None:
    """Tests changing both sort metric and limit for top stats"""
    start_dt = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    params = {"limit": 35, "metric": "last_visit"}
    response = await client.get("/stats", params=params)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 35
    assert [datetime.fromisoformat(d["last_visit"]) for d in data] == [start_dt - timedelta(hours=i) for i in range(35)]
    assert [d["visits"] for d in data] == list(range(35))


@pytest.mark.usefixtures("shortlink_list_with_stats")
async def test_top_stats_invalid_metric(client: AsyncClient) -> None:
    """Tests requesting an invalid metric returns an error"""
    params = {"metric": "invalid"}
    response = await client.get("/stats", params=params)
    data = response.json()

    assert response.status_code == 422
    assert data


@pytest.mark.usefixtures("shortlink_list_with_stats")
@pytest.mark.parametrize("limit", (-10, 1000))
async def test_top_stats_invalid_limit(client: AsyncClient, limit: int) -> None:
    """Tests requesting an invalid limit returns an error"""
    params = {"limit": limit}
    response = await client.get("/stats", params=params)
    data = response.json()

    assert response.status_code == 422
    assert data


async def test_get_stats_for_slug(client: AsyncClient, shortlink_with_stats: Shortlink) -> None:
    """Tests getting the stats for a shortlink that has stats"""
    response = await client.get(f"/stats/{shortlink_with_stats.slug}")
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "slug": shortlink_with_stats.slug,
        "short_url": f"http://test/{shortlink_with_stats.slug}",
        "long_url": "https://www.example.com/very/long/url",
        "visits": 10,
        "last_visit": "2025-01-01T12:00:00Z",
    }


async def test_get_stats_for_slug_without_stats(client: AsyncClient, shortlink: Shortlink) -> None:
    """Tests getting the stats for a shortlink that has does not yet have any stats"""
    response = await client.get(f"/stats/{shortlink.slug}")
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "slug": shortlink.slug,
        "short_url": shortlink.short_url,
        "long_url": shortlink.long_url,
        "visits": 0,
        "last_visit": None,
    }


async def test_get_stats_for_slug_does_not_exist(client: AsyncClient) -> None:
    """Tests getting the stats for a slug that does not exist returns an error"""
    slug = shortuuid.encode(uuid4())
    response = await client.get(f"/stats/{slug}")
    data = response.json()

    assert response.status_code == 404
    assert data == {"detail": "Not Found"}


async def test_get_stats_for_invalid_slug(client: AsyncClient) -> None:
    """Tests getting the stats for an invalid slug returns an error"""
    response = await client.get("/stats/invalid")
    data = response.json()

    assert response.status_code == 404
    assert data == {"detail": "Not Found"}
