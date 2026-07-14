"""
Router: /users — User Profile Endpoints
=========================================
Auth-adjacent endpoints for managing user profiles.
Supabase Auth handles authentication; these manage the N.A.R.I-specific
`users` table fields (gender, trust_score) from DESIGN.md §4.
"""

from fastapi import APIRouter

from app.schemas.user_schemas import UserProfile, UserCreate

router = APIRouter()


@router.post("/users", response_model=UserProfile)
async def create_user(payload: UserCreate):
    """
    Register a new user profile after Supabase Auth sign-up.
    Only collects gender as the demographic input (§3 M_demo).
    """
    # TODO: Wire to data.crud.users
    return UserProfile(
        user_id="00000000-0000-0000-0000-000000000000",
        gender=payload.gender,
        trust_score=1.0,
    )


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Retrieve a user profile by their Supabase Auth UUID."""
    # TODO: Wire to data.crud.users
    return UserProfile(
        user_id=user_id,
        gender="unknown",
        trust_score=1.0,
    )
