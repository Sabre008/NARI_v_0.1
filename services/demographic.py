"""
Demographic Context Matrix (M_demo)
=====================================
DESIGN.md §3: Adjusts safety perception based on gender and time of day.
Backed by NCRB crime data.

    Male   / Day  (8 AM – 8 PM):  1.00
    Male   / Night (8 PM – 8 AM): 0.80
    Female / Day  (8 AM – 8 PM):  0.90
    Female / Night (8 PM – 8 AM): 0.67
"""

from __future__ import annotations

# ── M_demo Lookup Table ────────────────────────────────
# Keys: (gender, time_period)
_M_DEMO: dict[tuple[str, str], float] = {
    ("male", "day"):    1.00,
    ("male", "night"):  0.80,
    ("female", "day"):  0.90,
    ("female", "night"): 0.67,
}

# Day = 08:00–19:59, Night = 20:00–07:59
DAY_START_HOUR = 8
DAY_END_HOUR = 20  # exclusive


def _classify_time(hour: int) -> str:
    """Classify an hour (0–23) as 'day' or 'night'."""
    if DAY_START_HOUR <= hour < DAY_END_HOUR:
        return "day"
    return "night"


def get_demographic_multiplier(
    gender: str,
    current_hour: int,
) -> float:
    """
    Look up the M_demo multiplier for a given gender and time.

    Parameters
    ----------
    gender : str
        'male' or 'female'. Case-insensitive. Defaults to 'male' for
        unknown values (conservative approach).
    current_hour : int
        Current hour of day (0–23).

    Returns
    -------
    float
        Demographic multiplier M_demo.
    """
    g = gender.strip().lower()
    if g not in ("male", "female"):
        g = "male"  # Conservative default

    period = _classify_time(current_hour)
    return _M_DEMO[(g, period)]
