"""
Geocoder — Map NER-extracted location text to H3 cells
=======================================================
DESIGN.md §2B: Converts location strings (e.g., "Kankarbagh", "Gandhi Maidan")
to H3 centroid_ids for penalty application.

Strategy:
    1. Maintain a local lookup table of known Patna landmarks → (lat, lng).
    2. Fall back to a geocoding API for unknown names.
    3. Convert (lat, lng) → H3 index at the configured resolution.
"""

from __future__ import annotations

import h3

# ── H3 resolution for the project grid (see notebooks/01) ──
H3_RESOLUTION = 8

# ── Known Patna Landmarks (pre-seeded lookup) ──────────
# Format: { "lowercase_name": (latitude, longitude) }
PATNA_LANDMARKS: dict[str, tuple[float, float]] = {
    "gandhi maidan": (25.6117, 85.1390),
    "patna junction": (25.6093, 85.1376),
    "kankarbagh": (25.5942, 85.1748),
    "boring road": (25.6070, 85.1267),
    "rajendra nagar": (25.6150, 85.1141),
    "patna city": (25.5857, 85.1878),
    "danapur": (25.6247, 85.0486),
    "bailey road": (25.6134, 85.1028),
    "ashok rajpath": (25.6197, 85.1640),
    "patna university": (25.6156, 85.1642),
    # TODO: Expand with more localities
}


def location_to_h3(
    location_name: str,
    resolution: int = H3_RESOLUTION,
) -> int | None:
    """
    Convert a location name to an H3 cell index.

    Parameters
    ----------
    location_name : str
        Place name extracted by NER.
    resolution : int
        H3 resolution level.

    Returns
    -------
    int | None
        H3 cell index as integer, or None if the location is unknown.
    """
    key = location_name.strip().lower()

    coords = PATNA_LANDMARKS.get(key)
    if coords is None:
        # TODO: Fall back to geocoding API (Nominatim / Google)
        return None

    lat, lng = coords
    h3_index = h3.latlng_to_cell(lat, lng, resolution)
    return int(h3_index, 16) if isinstance(h3_index, str) else h3_index


def coords_to_h3(
    lat: float,
    lng: float,
    resolution: int = H3_RESOLUTION,
) -> str:
    """
    Convert raw lat/lng to an H3 hex string.

    Returns
    -------
    str
        H3 cell index as a hex string.
    """
    return h3.latlng_to_cell(lat, lng, resolution)
