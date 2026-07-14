"""Integration tests for FastAPI endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.anyio
async def test_health_check():
    """GET /health should return 200 with service info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "nari-api"


@pytest.mark.anyio
async def test_route_endpoint_placeholder():
    """POST /api/v1/route should return a response (even if placeholder)."""
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
    assert response.status_code == 200
