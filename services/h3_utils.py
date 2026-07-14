"""
H3 Hexagonal Grid Utilities
=============================
Common H3 operations used across the codebase:
    - lat/lng ↔ H3 cell conversion
    - Neighbour ring queries
    - Cell boundary polygon extraction (for Folium rendering)
"""

from __future__ import annotations

import h3

# Project-wide H3 resolution (≈ 460 m edge length at resolution 8)
H3_RESOLUTION = 8


def latlng_to_cell(lat: float, lng: float, resolution: int = H3_RESOLUTION) -> str:
    """Convert a WGS-84 coordinate to an H3 cell index string."""
    return h3.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(cell: str) -> tuple[float, float]:
    """Return the centroid (lat, lng) of an H3 cell."""
    return h3.cell_to_latlng(cell)


def cell_to_boundary(cell: str) -> list[tuple[float, float]]:
    """
    Return the boundary polygon vertices of an H3 cell as
    [(lat, lng), ...] — suitable for Folium polygon overlays.
    """
    return list(h3.cell_to_boundary(cell))


def get_neighbours(cell: str, ring_size: int = 1) -> list[str]:
    """
    Return H3 cells in a k-ring around the given cell.

    Parameters
    ----------
    ring_size : int
        Number of rings outward. 1 = immediate neighbours (6 cells).
    """
    return list(h3.grid_disk(cell, ring_size))


def cells_in_bbox(
    north: float,
    south: float,
    east: float,
    west: float,
    resolution: int = H3_RESOLUTION,
) -> list[str]:
    """
    Generate all H3 cells whose centroids fall within a bounding box.

    This is a brute-force approach suitable for city-scale areas.
    For production, consider using h3.polygon_to_cells with a proper polygon.
    """
    # Use the polyfill approach with a rectangular polygon
    polygon = h3.LatLngPoly(
        [(north, west), (north, east), (south, east), (south, west)]
    )
    return list(h3.polygon_to_cells(polygon, resolution))
