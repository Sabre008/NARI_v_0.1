"""
Time-Decay Rating Computation
===============================
DESIGN.md §2C:  W_report = Rating · e^(−λt)

Verified crowd ratings naturally diminish over time so that stale
reports don't permanently skew the safety score.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from app.config import settings


def compute_decayed_weight(
    rating: int,
    report_time: datetime,
    current_time: datetime | None = None,
    decay_lambda: float | None = None,
) -> float:
    """
    Apply exponential time-decay to a crowd safety rating.

    Formula:  W = rating · e^(−λ · t_hours)

    Parameters
    ----------
    rating : int
        Raw safety rating (1–5).
    report_time : datetime
        When the report was submitted (must be timezone-aware).
    current_time : datetime | None
        Override for "now". Defaults to UTC now.
    decay_lambda : float | None
        Decay constant λ. Defaults to settings.DECAY_LAMBDA.

    Returns
    -------
    float
        Decayed weight W ≥ 0.
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    if decay_lambda is None:
        decay_lambda = settings.DECAY_LAMBDA

    # Time difference in hours
    delta = current_time - report_time
    t_hours = delta.total_seconds() / 3600.0

    return rating * math.exp(-decay_lambda * t_hours)


def aggregate_crowd_score(
    ratings: list[tuple[int, datetime]],
    current_time: datetime | None = None,
) -> float:
    """
    Compute the aggregate decayed crowd score (Crowd_decay) for a grid cell.

    Parameters
    ----------
    ratings : list[tuple[int, datetime]]
        List of (rating_score, timestamp) pairs for verified reports.

    Returns
    -------
    float
        Normalised crowd score in [0, 1]. Returns 0.5 if no ratings exist.
    """
    if not ratings:
        return 0.5  # Neutral default

    weights = [
        compute_decayed_weight(r, t, current_time) for r, t in ratings
    ]

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.5

    # Weighted average normalised to [0, 1] (since max rating = 5)
    weighted_sum = sum(w for w in weights)
    max_possible = sum(5 * math.exp(-settings.DECAY_LAMBDA * 0) for _ in ratings)

    return min(weighted_sum / max_possible, 1.0)
