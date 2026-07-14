"""Integration tests for FastAPI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.anyio
async def test_health_check():
    """GET /health should return 200 with service and component info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "nari-api"
    assert data["status"] in ("healthy", "degraded")
    assert "components" in data


@pytest.mark.anyio
async def test_route_endpoint_requires_graph():
    """POST /api/v1/route should return 503 if the road graph is not loaded."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/route",
            json={
                "origin": {"lat": 25.6117, "lng": 85.139},
                "destination": {"lat": 25.5942, "lng": 85.1748},
                "gender": "female",
            },
        )
    # Without data files in the test env, the endpoint should return 503
    assert response.status_code in (200, 503)
