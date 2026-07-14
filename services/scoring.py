"""
Scoring Orchestrator
=====================
Merges outputs from all subsystems into the final S_total per grid cell:
    - S_infra  (models.safety_dnn.predict)
    - M_demo   (services.demographic)
    - Crowd    (models.trust_engine.decay)
    - News     (data.crud.hazards)
"""

from __future__ import annotations

from datetime import datetime

from routing.cost_function import compute_edge_safety
from services.demographic import get_demographic_multiplier
from models.trust_engine.decay import aggregate_crowd_score


def compute_cell_score(
    s_infra: float,
    gender: str,
    current_hour: int,
    crowd_ratings: list[tuple[int, datetime]] | None = None,
    news_severity: float = 0.0,
) -> float:
    """
    Compute the full S_total for a single H3 cell.

    Parameters
    ----------
    s_infra : float
        Base infrastructure safety score [0, 1].
    gender : str
        'male' or 'female'.
    current_hour : int
        Hour of day (0–23).
    crowd_ratings : list[tuple[int, datetime]] | None
        Verified (rating, timestamp) pairs for this cell.
    news_severity : float
        Active hazard severity [0, 1].

    Returns
    -------
    float
        Composite S_total ∈ [0, 1].
    """
    m_demo = get_demographic_multiplier(gender, current_hour)
    crowd_decay = aggregate_crowd_score(crowd_ratings or [])

    return compute_edge_safety(
        s_infra=s_infra,
        m_demo=m_demo,
        crowd_decay=crowd_decay,
        news_severity=news_severity,
    )
