"""
Distance Constraint Enforcement
=================================
DESIGN.md §3:
    Distance_candidate ≤ 1.25 × Distance_shortest

Filters candidate paths to ensure we never suggest routes that are
excessively longer than the shortest path, even if they are safer.
"""

from __future__ import annotations

import networkx as nx

from app.config import settings
from routing.yen_ksp import path_total_weight


def filter_by_distance_constraint(
    G: nx.MultiDiGraph | nx.DiGraph,
    paths: list[list[int]],
    shortest_distance: float | None = None,
    max_detour_factor: float | None = None,
    weight: str = "length",
) -> list[tuple[list[int], float]]:
    """
    Filter candidate paths by the 1.25× distance constraint.

    Parameters
    ----------
    G : Graph
        Road network with edge weights.
    paths : list[list[int]]
        Candidate paths (from Yen's KSP).
    shortest_distance : float | None
        Pre-computed shortest path distance. If None, uses paths[0].
    max_detour_factor : float | None
        Maximum allowed ratio. Default from settings.MAX_DETOUR_FACTOR.
    weight : str
        Edge attribute for distance.

    Returns
    -------
    list[tuple[list[int], float]]
        Filtered (path, distance) pairs that satisfy the constraint.
    """
    if max_detour_factor is None:
        max_detour_factor = settings.MAX_DETOUR_FACTOR

    if not paths:
        return []

    # Compute shortest distance from the first path if not provided
    if shortest_distance is None:
        shortest_distance = path_total_weight(G, paths[0], weight=weight)

    max_allowed = max_detour_factor * shortest_distance

    valid: list[tuple[list[int], float]] = []
    for path in paths:
        dist = path_total_weight(G, path, weight=weight)
        if dist <= max_allowed:
            valid.append((path, dist))

    return valid


def select_safest_constrained(
    G: nx.MultiDiGraph | nx.DiGraph,
    paths: list[list[int]],
    safety_scores: dict[int, float],
    weight: str = "length",
) -> tuple[list[int], float, float] | None:
    """
    From distance-constrained paths, select the one with the highest
    average safety score.

    Returns
    -------
    tuple | None
        (best_path, distance, avg_safety) or None if no valid paths.
    """
    constrained = filter_by_distance_constraint(G, paths, weight=weight)

    if not constrained:
        return None

    best = None
    best_safety = -1.0

    for path, dist in constrained:
        scores = [safety_scores.get(node, 0.5) for node in path]
        avg_safety = sum(scores) / len(scores) if scores else 0.0

        if avg_safety > best_safety:
            best_safety = avg_safety
            best = (path, dist, avg_safety)

    return best
