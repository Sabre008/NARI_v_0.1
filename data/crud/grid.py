"""
CRUD: locations_grid table
============================
DESIGN.md §4: centroid_id (H3 index), geometry, base_infra_score, poi_metadata.
"""

from __future__ import annotations

from supabase import Client

TABLE = "locations_grid"


def upsert_cell(
    client: Client,
    centroid_id: int,
    base_infra_score: float,
    poi_metadata: dict | None = None,
) -> dict:
    """Insert or update an H3 grid cell record."""
    row = {
        "centroid_id": centroid_id,
        "base_infra_score": base_infra_score,
        "poi_metadata": poi_metadata or {},
    }
    return (
        client.table(TABLE)
        .upsert(row, on_conflict="centroid_id")
        .execute()
        .data
    )


def get_cell(client: Client, centroid_id: int) -> dict | None:
    """Fetch a single grid cell by H3 index."""
    result = (
        client.table(TABLE)
        .select("*")
        .eq("centroid_id", centroid_id)
        .maybe_single()
        .execute()
    )
    return result.data


def get_all_cells(client: Client) -> list[dict]:
    """Fetch all grid cells (for batch scoring / map overlay)."""
    return client.table(TABLE).select("*").execute().data


def bulk_upsert_cells(client: Client, rows: list[dict]) -> dict:
    """Bulk upsert grid cell records."""
    return (
        client.table(TABLE)
        .upsert(rows, on_conflict="centroid_id")
        .execute()
        .data
    )
