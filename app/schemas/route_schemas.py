"""
Pydantic schemas for the /route endpoint.
"""

from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    """A geographic coordinate (WGS-84)."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class RouteRequest(BaseModel):
    """Payload for POST /route."""
    origin: Coordinate
    destination: Coordinate
    gender: str = Field("male", description="User demographic: 'male' or 'female'")
    time_of_day: str | None = Field(
        None,
        description="ISO-8601 time string. If omitted, server uses current time.",
    )
    k_paths: int = Field(5, ge=1, le=20, description="Number of candidate paths")


class PathSegment(BaseModel):
    """One segment of the returned route with safety metadata."""
    coordinates: list[Coordinate]
    centroid_id: int = Field(..., description="H3 hex cell this segment crosses")
    segment_safety: float = Field(..., ge=0.0, le=1.0)
    distance_m: float


class RouteResponse(BaseModel):
    """Response from POST /route."""
    status: str
    message: str | None = None
    path_segments: list[PathSegment] = []
    total_distance_km: float = 0.0
    total_safety_score: float = 0.0
    detour_factor: float | None = Field(
        None,
        description="Ratio of chosen path distance to shortest path distance",
    )
