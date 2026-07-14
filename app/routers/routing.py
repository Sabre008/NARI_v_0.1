"""
Router: /route — Constrained Safe-Path Endpoint
=================================================
Accepts an origin/destination pair, user demographics, and returns
the safest route within the 1.25x distance constraint (DESIGN.md §3).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import h3
import numpy as np
import osmnx as ox
from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.schemas.route_schemas import (
    Coordinate,
    PathSummary,
    RouteRequest,
    RouteResponse,
)
from routing.cost_function import compute_edge_safety, safety_to_cost
from routing.yen_ksp import k_shortest_paths, path_total_weight
from services.demographic import get_demographic_multiplier

logger = logging.getLogger("nari.routing")
router = APIRouter()

H3_RESOLUTION = 8
ALPHA = settings.ALPHA_CROWD
BETA = settings.BETA_NEWS
CROWD_BASELINE = 0.5
NEWS_BASELINE = 0.0


def _resolve_hour(time_of_day: str | None) -> int:
    """Parse the optional time_of_day field, defaulting to server time."""
    if time_of_day:
        try:
            return int(time_of_day.split(":")[0].split("T")[-1])
        except (ValueError, IndexError):
            pass
    return datetime.now(timezone.utc).hour


def _stamp_safety_costs(
    graph,
    node_safety: dict[int, float],
    m_demo: float,
) -> None:
    """Write a `safety_cost` attribute onto every edge in the graph."""
    for u, v, _key, data in graph.edges(keys=True, data=True):
        s_infra = (node_safety.get(u, 0.3) + node_safety.get(v, 0.3)) / 2.0
        s_total = compute_edge_safety(
            s_infra=s_infra,
            m_demo=m_demo,
            crowd_decay=CROWD_BASELINE,
            news_severity=NEWS_BASELINE,
            alpha=ALPHA,
            beta=BETA,
        )
        data["safety_cost"] = safety_to_cost(s_total)


def _path_to_coords(graph, path: list[int]) -> list[Coordinate]:
    """Convert a node-ID path to a list of Coordinate objects."""
    coords = []
    for node in path:
        data = graph.nodes[node]
        coords.append(Coordinate(lat=data["y"], lng=data["x"]))
    return coords


def _avg_path_safety(
    path: list[int],
    node_safety: dict[int, float],
    m_demo: float,
) -> float:
    """Compute the average S_total along a path."""
    if not path:
        return 0.0
    scores = [node_safety.get(n, 0.3) for n in path]
    avg_infra = float(np.mean(scores))
    return compute_edge_safety(
        s_infra=avg_infra,
        m_demo=m_demo,
        crowd_decay=CROWD_BASELINE,
        news_severity=NEWS_BASELINE,
        alpha=ALPHA,
        beta=BETA,
    )


@router.post("/route", response_model=RouteResponse)
async def get_safe_route(payload: RouteRequest, request: Request):
    """
    Compute the safest navigable route from origin to destination.

    Pipeline:
    1. Retrieve pre-loaded graph and node safety map from app.state
    2. Resolve origin/destination to nearest graph nodes
    3. Stamp safety_cost on edges using the demographic multiplier
    4. Run Yen's KSP with both distance and safety weights
    5. Filter by 1.25x distance constraint
    6. Return the safest constrained path alongside the fastest path
    """
    graph = request.app.state.graph
    node_safety = request.app.state.node_safety

    if graph is None:
        raise HTTPException(status_code=503, detail="Road graph not loaded")
    if not node_safety:
        raise HTTPException(status_code=503, detail="Safety scores not available")

    # Resolve demographic multiplier
    hour = _resolve_hour(payload.time_of_day)
    m_demo = get_demographic_multiplier(payload.gender, hour)

    # Stamp safety costs onto edges
    _stamp_safety_costs(graph, node_safety, m_demo)

    # Snap origin and destination to nearest graph nodes
    try:
        origin_node = ox.nearest_nodes(
            graph, payload.origin.lng, payload.origin.lat,
        )
        dest_node = ox.nearest_nodes(
            graph, payload.destination.lng, payload.destination.lat,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not snap coordinates to road network: {exc}",
        )

    if origin_node == dest_node:
        raise HTTPException(
            status_code=400,
            detail="Origin and destination resolve to the same node",
        )

    # Generate candidate paths
    k = payload.k_paths
    paths_by_dist = k_shortest_paths(graph, origin_node, dest_node, k=k, weight="length")
    paths_by_safe = k_shortest_paths(graph, origin_node, dest_node, k=k, weight="safety_cost")

    if not paths_by_dist:
        raise HTTPException(status_code=404, detail="No route found between the given points")

    # Merge all unique candidates
    all_candidates: dict[tuple, list[int]] = {}
    for p in paths_by_dist + paths_by_safe:
        all_candidates[tuple(p)] = p

    # Evaluate each candidate
    fastest_distance = path_total_weight(graph, paths_by_dist[0], weight="length")
    max_allowed = settings.MAX_DETOUR_FACTOR * fastest_distance

    fastest_path = paths_by_dist[0]
    fastest_safety = _avg_path_safety(fastest_path, node_safety, m_demo)

    best_safest = None
    best_safest_score = -1.0
    candidates_within_budget = 0

    for path in all_candidates.values():
        dist = path_total_weight(graph, path, weight="length")
        if dist > max_allowed:
            continue
        candidates_within_budget += 1
        score = _avg_path_safety(path, node_safety, m_demo)
        if score > best_safest_score:
            best_safest_score = score
            best_safest = (path, dist, score)

    # Fallback: if no safety-optimised path found, use fastest
    if best_safest is None:
        best_safest = (fastest_path, fastest_distance, fastest_safety)
        candidates_within_budget = 1

    safest_path, safest_dist, safest_score = best_safest
    detour = safest_dist / fastest_distance if fastest_distance > 0 else 1.0

    return RouteResponse(
        status="ok",
        safest_path=PathSummary(
            coordinates=_path_to_coords(graph, safest_path),
            total_distance_m=round(safest_dist, 1),
            avg_safety_score=round(safest_score, 4),
            node_count=len(safest_path),
        ),
        fastest_path=PathSummary(
            coordinates=_path_to_coords(graph, fastest_path),
            total_distance_m=round(fastest_distance, 1),
            avg_safety_score=round(fastest_safety, 4),
            node_count=len(fastest_path),
        ),
        detour_factor=round(detour, 3),
        candidates_evaluated=len(all_candidates),
        candidates_within_budget=candidates_within_budget,
        demographic=f"{payload.gender}/{hour:02d}:00",
        m_demo=m_demo,
    )
