"""
Supabase Client Wrapper
========================
Provides a configured Supabase client for all CRUD operations.
"""

from __future__ import annotations

from supabase import create_client, Client


def get_supabase_client(url: str, key: str) -> Client:
    """
    Create and return a Supabase client.

    Parameters
    ----------
    url : str
        Supabase project URL.
    key : str
        Supabase anon or service-role key.

    Returns
    -------
    Client
        Configured Supabase client.
    """
    return create_client(url, key)
