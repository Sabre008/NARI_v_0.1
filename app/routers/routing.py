"""
Router: /route — Constrained Safe-Path Endpoint
=================================================
Accepts an origin/destination pair, user demographics, and returns
the safest route within the 1.25× distance constraint (DESIGN.md §3).
"""

from fastapi import APIRouter, Depends

from app.schemas.route_schemas import RouteRequest, RouteResponse

router = APIRouter()


@router.post("/route", response_model=RouteResponse)
async def get_safe_route(payload: RouteRequest):
    """
    Compute the safest navigable route from origin to destination.

    Pipeline:
    1. Build/load the Patna road graph (routing.graph_builder).
    2. Find K shortest paths via Yen's algorithm (routing.yen_ksp).
    3. Score each candidate with S_total (services.scoring).
    4. Enforce the 1.25× distance constraint (routing.constraints).
    5. Return the best candidate with segment-level safety metadata.
    """
    # TODO: Wire to routing + services layer
    return RouteResponse(
        status="not_implemented",
        message="Route computation not yet wired.",
        path_segments=[],
        total_distance_km=0.0,
        total_safety_score=0.0,
    )
