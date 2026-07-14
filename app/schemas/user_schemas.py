"""
Pydantic schemas for user profile endpoints.
"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Payload for POST /users."""
    user_id: str = Field(..., description="Supabase Auth UUID")
    gender: str = Field(..., description="'male' or 'female'")


class UserProfile(BaseModel):
    """User profile response model (§4 users table)."""
    user_id: str
    gender: str
    trust_score: float = Field(1.0, ge=0.0, le=1.0)
