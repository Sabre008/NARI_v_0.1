"""
Router: /route — Constrained Safe-Path Endpoint
=================================================
Accepts an origin/destination pair, user demographics, and returns
the safest route within the 1.25x distance constraint (DESIGN.md §3).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
import urllib.parse

import h3
import numpy as np
import osmnx as ox
from fastapi import APIRouter, HTTPException, Request
from geopy.geocoders import Nominatim

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
from supabase import create_client, Client
from models.nlp_hazard.scraper import fetch_all_feeds
from models.nlp_hazard.pipeline import load_pipeline, classify_article

logger = logging.getLogger("nari.routing")
router = APIRouter()

H3_RESOLUTION = 8
ALPHA = settings.ALPHA_CROWD
BETA = settings.BETA_NEWS
CROWD_BASELINE = 0.0
NEWS_BASELINE = 0.0

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

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
    active_hazards: dict[str, float] | None = None,
) -> None:
    """Write a `safety_cost` attribute onto every edge in the graph."""
    for u, v, _key, data in graph.edges(keys=True, data=True):
        s_infra = (node_safety.get(u, 0.3) + node_safety.get(v, 0.3)) / 2.0
        
        # Determine cells for u and v
        cell_u = h3.latlng_to_cell(graph.nodes[u]['y'], graph.nodes[u]['x'], H3_RESOLUTION)
        cell_v = h3.latlng_to_cell(graph.nodes[v]['y'], graph.nodes[v]['x'], H3_RESOLUTION)
        
        s_total = compute_edge_safety(
            s_infra=s_infra,
            m_demo=m_demo,
            crowd_decay=CROWD_BASELINE,
            news_severity=NEWS_BASELINE,
            alpha=ALPHA,
            beta=BETA,
            edge_cells=[cell_u, cell_v],
            active_hazards=active_hazards,
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
    graph,
    path: list[int],
    node_safety: dict[int, float],
    m_demo: float,
    active_hazards: dict[str, float] | None = None,
) -> float:
    """Compute the average S_total along a path."""
    if not path:
        return 0.0
    scores = [node_safety.get(n, 0.3) for n in path]
    avg_infra = float(np.mean(scores))
    
    edge_cells = []
    for node in path:
        cell = h3.latlng_to_cell(graph.nodes[node]['y'], graph.nodes[node]['x'], H3_RESOLUTION)
        edge_cells.append(cell)
        
    return compute_edge_safety(
        s_infra=avg_infra,
        m_demo=m_demo,
        crowd_decay=CROWD_BASELINE,
        news_severity=NEWS_BASELINE,
        alpha=ALPHA,
        beta=BETA,
        edge_cells=edge_cells,
        active_hazards=active_hazards,
    )


@router.post("/route", response_model=RouteResponse)
async def get_safe_route(payload: RouteRequest, request: Request):
    """
    Compute the safest navigable route from origin to destination.
    """
    graph = request.app.state.graph
    node_safety = request.app.state.node_safety
    
    if graph is None:
        raise HTTPException(status_code=503, detail="Road graph not loaded")
    if not node_safety:
        raise HTTPException(status_code=503, detail="Safety scores not available")

    route_hazards_meta = []
    
    # 1. On-the-spot Targeted NLP Scraper
    active_news_hazards = {}
    if payload.origin_name or payload.dest_name:
        query_parts = []
        if payload.origin_name:
            query_parts.append(payload.origin_name.split(",")[0].strip())
        if payload.dest_name:
            query_parts.append(payload.dest_name.split(",")[0].strip())
            
        search_query = " OR ".join(query_parts) + " Patna Bihar"
        encoded_query = urllib.parse.quote_plus(search_query)
        feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        try:
            articles = fetch_all_feeds(feed_urls=[feed_url])
            classifier, ner_pipeline = load_pipeline()
            geocoder = Nominatim(user_agent="NARI_Patna_App", timeout=5)
            
            for article in articles:
                result = classify_article(article.title, classifier, ner_pipeline)
                if result is None:
                    continue
                    
                for loc in result.locations:
                    try:
                        geo = geocoder.geocode(f"{loc}, Patna, Bihar, India", exactly_one=True)
                        if geo:
                            hex_id = h3.latlng_to_cell(geo.latitude, geo.longitude, H3_RESOLUTION)
                            active_news_hazards[hex_id] = max(
                                active_news_hazards.get(hex_id, 0.0),
                                result.severity
                            )
                            route_hazards_meta.append({
                                "type": "news",
                                "h3_index": hex_id,
                                "severity": result.severity,
                                "description": f"News hazard at {loc}: {result.headline}"
                            })
                    except Exception as e:
                        logger.error(f"Failed to geocode {loc}: {e}")
        except Exception as e:
            logger.error(f"Failed targeted NLP scraper: {e}")

    # 2. Fetch crowd reports with time decay
    active_crowd_hazards = {}
    try:
        supabase = get_supabase()
        yesterday = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        response = supabase.table("reports").select("h3_index, created_at, severity_rating, hazard_type").gte("created_at", yesterday).execute()
        
        for report in response.data:
            report_time = datetime.fromisoformat(report["created_at"].replace('Z', '+00:00'))
            hours_since = (datetime.now(timezone.utc) - report_time).total_seconds() / 3600.0
            decay = max(0.0, 1.0 - (hours_since / 24.0))
            
            normalized_severity = (report["severity_rating"] - 1) / 4.0
            crowd_score = normalized_severity * decay
            
            if crowd_score > 0:
                h3_idx = report["h3_index"]
                active_crowd_hazards[h3_idx] = max(active_crowd_hazards.get(h3_idx, 0.0), crowd_score)
                
                route_hazards_meta.append({
                    "type": "crowd",
                    "h3_index": h3_idx,
                    "severity": round(crowd_score, 3),
                    "description": f"Crowd report: {report['hazard_type']} ({round(hours_since, 1)}h ago)"
                })
    except Exception as e:
        logger.error(f"Failed to fetch crowd reports: {e}")

    # Merge hazards for cost function
    merged_hazards = {}
    for h3_idx, sev in active_news_hazards.items():
        merged_hazards[h3_idx] = sev
        
    for h3_idx, sev in active_crowd_hazards.items():
        merged_hazards[h3_idx] = max(merged_hazards.get(h3_idx, 0.0), sev)

    # Resolve demographic multiplier
    hour = _resolve_hour(payload.time_of_day)
    m_demo = get_demographic_multiplier(payload.gender, hour)

    # Stamp safety costs onto edges
    _stamp_safety_costs(graph, node_safety, m_demo, merged_hazards)

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
    fastest_safety = _avg_path_safety(graph, fastest_path, node_safety, m_demo, merged_hazards)

    best_safest = None
    best_safest_score = -1.0
    candidates_within_budget = 0

    for path in all_candidates.values():
        dist = path_total_weight(graph, path, weight="length")
        if dist > max_allowed:
            continue
        candidates_within_budget += 1
        score = _avg_path_safety(graph, path, node_safety, m_demo, merged_hazards)
        if score > best_safest_score:
            best_safest_score = score
            best_safest = (path, dist, score)

    # Fallback: if no safety-optimised path found, use fastest
    if best_safest is None:
        best_safest = (fastest_path, fastest_distance, fastest_safety)
        candidates_within_budget = 1

    safest_path, safest_dist, safest_score = best_safest
    detour = safest_dist / fastest_distance if fastest_distance > 0 else 1.0

    avg_news_penalty = sum(active_news_hazards.values()) / len(active_news_hazards) if active_news_hazards else 0.0
    avg_crowd_penalty = sum(active_crowd_hazards.values()) / len(active_crowd_hazards) if active_crowd_hazards else 0.0

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
        avg_news_penalty=round(avg_news_penalty, 4),
        avg_crowd_penalty=round(avg_crowd_penalty, 4),
        route_hazards=route_hazards_meta
    )
