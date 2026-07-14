"""
CRUD: crowd_reports table
===========================
DESIGN.md §4: report_id, centroid_id, user_id, rating_score, timestamp, is_verified.
"""

from __future__ import annotations

from supabase import Client

TABLE = "crowd_reports"


def insert_report(
    client: Client,
    centroid_id: int,
    user_id: str,
    rating_score: int,
    is_verified: bool = False,
) -> dict:
    """Insert a new crowd safety report."""
    return (
        client.table(TABLE)
        .insert({
            "centroid_id": centroid_id,
            "user_id": user_id,
            "rating_score": rating_score,
            "is_verified": is_verified,
        })
        .execute()
        .data
    )


def get_reports_for_cell(
    client: Client,
    centroid_id: int,
    verified_only: bool = True,
) -> list[dict]:
    """Fetch crowd reports for a specific grid cell."""
    query = client.table(TABLE).select("*").eq("centroid_id", centroid_id)
    if verified_only:
        query = query.eq("is_verified", True)
    return query.order("timestamp", desc=True).execute().data


def mark_verified(client: Client, report_id: int, verified: bool = True) -> dict:
    """Update the verification status of a report."""
    return (
        client.table(TABLE)
        .update({"is_verified": verified})
        .eq("report_id", report_id)
        .execute()
        .data
    )
