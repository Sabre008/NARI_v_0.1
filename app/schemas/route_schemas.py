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
    centroid_id: str = Field(..., description="H3 hex cell this segment crosses")
    segment_safety: float = Field(..., ge=0.0, le=1.0)
    distance_m: float


class PathSummary(BaseModel):
    """Summary of a single candidate route."""
    coordinates: list[Coordinate] = Field(default_factory=list)
    total_distance_m: float = 0.0
    avg_safety_score: float = 0.0
    node_count: int = 0


class RouteResponse(BaseModel):
    """Response from POST /route."""
    status: str
    message: str | None = None
    safest_path: PathSummary = Field(
        default_factory=PathSummary,
        description="Recommended route: highest S_total within 1.25x distance budget",
    )
    fastest_path: PathSummary = Field(
        default_factory=PathSummary,
        description="Shortest distance route for comparison",
    )
    detour_factor: float | None = Field(
        None,
        description="Ratio of safest path distance to fastest path distance",
    )
    candidates_evaluated: int = 0
    candidates_within_budget: int = 0
    demographic: str | None = None
    m_demo: float | None = None
