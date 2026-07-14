"""
CRUD: news_hazards table
==========================
DESIGN.md §4: incident_id, centroid_id, severity_score, expiry_timer.
"""

from __future__ import annotations

from datetime import datetime, timezone

from supabase import Client

TABLE = "news_hazards"


def upsert_hazard(
    client: Client,
    centroid_id: int,
    severity_score: float,
    expiry_timer: datetime,
) -> dict:
    """Insert or update a hazard incident for a grid cell."""
    return (
        client.table(TABLE)
        .upsert(
            {
                "centroid_id": centroid_id,
                "severity_score": severity_score,
                "expiry_timer": expiry_timer.isoformat(),
            },
            on_conflict="centroid_id",
        )
        .execute()
        .data
    )


def get_active_hazards(client: Client) -> list[dict]:
    """Fetch all hazards whose expiry_timer has not yet passed."""
    now = datetime.now(timezone.utc).isoformat()
    return (
        client.table(TABLE)
        .select("*")
        .gte("expiry_timer", now)
        .execute()
        .data
    )


def get_hazard_for_cell(client: Client, centroid_id: int) -> dict | None:
    """Fetch the active hazard for a specific cell (if any)."""
    now = datetime.now(timezone.utc).isoformat()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("centroid_id", centroid_id)
        .gte("expiry_timer", now)
        .maybe_single()
        .execute()
    )
    return result.data


def purge_expired(client: Client) -> int:
    """Delete all expired hazard records. Returns count of purged rows."""
    now = datetime.now(timezone.utc).isoformat()
    result = (
        client.table(TABLE)
        .delete()
        .lt("expiry_timer", now)
        .execute()
    )
    return len(result.data)
