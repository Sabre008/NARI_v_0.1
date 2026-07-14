"""
CRUD: users table
==================
DESIGN.md §4: user_id (UUID PK), gender, trust_score, account_created.
"""

from __future__ import annotations

from supabase import Client

TABLE = "users"


def create_user(client: Client, user_id: str, gender: str) -> dict:
    """Insert a new user profile."""
    return (
        client.table(TABLE)
        .insert({"user_id": user_id, "gender": gender, "trust_score": 1.0})
        .execute()
        .data
    )


def get_user(client: Client, user_id: str) -> dict | None:
    """Fetch a user profile by UUID."""
    result = (
        client.table(TABLE)
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data


def update_trust_score(client: Client, user_id: str, new_score: float) -> dict:
    """Update a user's trust score."""
    return (
        client.table(TABLE)
        .update({"trust_score": new_score})
        .eq("user_id", user_id)
        .execute()
        .data
    )
