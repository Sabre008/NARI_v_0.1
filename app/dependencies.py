"""
N.A.R.I — Shared FastAPI Dependencies
=======================================
Dependency-injection callables used across routers.
Provides the Supabase client and any other shared resources.
"""

from functools import lru_cache

from app.config import settings
from data.supabase_client import get_supabase_client


@lru_cache(maxsize=1)
def get_db_client():
    """
    Return a cached Supabase client instance.
    Used as a FastAPI dependency via `Depends(get_db_client)`.
    """
    return get_supabase_client(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_KEY,
    )
