"""
Dynamic Cost Function — S_total
=================================
DESIGN.md §3:
    S_total = (S_infra · M_demo) + (α · Crowd_decay) − (β · News_severity)

This module computes per-edge safety costs used as weights in the
routing graph. Lower S_total = less safe = higher traversal cost.
"""

from __future__ import annotations

from app.config import settings


def compute_edge_safety(
    s_infra: float,
    m_demo: float,
    crowd_decay: float,
    news_severity: float = 0.0,
    alpha: float | None = None,
    beta: float | None = None,
    edge_cells: list[str] | None = None,
    active_hazards: dict[str, float] | None = None,
) -> float:
    """
    Compute the composite safety score for a single graph edge / H3 cell.

    Parameters
    ----------
    s_infra : float
        Base infrastructure safety score [0, 1].
    m_demo : float
        Demographic adjustment multiplier (from services.demographic).
    crowd_decay : float
        Time-decayed crowd rating score [0, 1].
    news_severity : float
        Current news hazard severity [0, 1]. 0 = no hazard.
    alpha : float
        Weight for crowd component. Default from settings.
    beta : float
        Weight for news component. Default from settings.
    edge_cells: list[str]
        H3 cells for the current edge's nodes.
    active_hazards: dict[str, float]
        Dictionary mapping H3 cell to max active hazard severity.

    Returns
    -------
    float
        S_total safety score. Higher = safer.
    """
    if alpha is None:
        alpha = settings.ALPHA_CROWD
    if beta is None:
        beta = settings.BETA_NEWS

    if edge_cells and active_hazards:
        hazard_penalty = 0.0
        for cell in edge_cells:
            hazard_penalty = max(hazard_penalty, active_hazards.get(cell, 0.0))
        news_severity = max(news_severity, hazard_penalty)

    s_total = (s_infra * m_demo) + (alpha * crowd_decay) - (beta * news_severity)

    # Clamp to [0, 1]
    return max(0.0, min(1.0, s_total))


def safety_to_cost(s_total: float) -> float:
    """
    Convert a safety score to a traversal cost for graph routing.

    The routing algorithm minimises cost, so safer edges must have
    *lower* cost. We invert the safety score:

        cost = 1.0 − S_total

    A perfectly safe edge (S_total = 1.0) has cost 0.
    A completely unsafe edge (S_total = 0.0) has cost 1.

    Returns
    -------
    float
        Traversal cost in [0, 1].
    """
    return 1.0 - s_total
