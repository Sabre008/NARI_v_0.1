"""
Pydantic schemas for the /parse_news endpoint.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class HazardEvent(BaseModel):
    """A single detected hazard incident."""
    centroid_id: str = Field(..., description="Affected H3 hex cell")
    severity_score: float = Field(..., ge=0.0, le=1.0)
    description: str
    source_url: str | None = None
    expiry: datetime | None = Field(
        None, description="When this hazard penalty expires"
    )


class NewsParseResponse(BaseModel):
    """Response from POST /parse_news."""
    status: str
    hazards_detected: int = 0
    incidents: list[HazardEvent] = []
