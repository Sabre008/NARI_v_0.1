"""
Pydantic schemas for crowdsource report endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ReportSubmission(BaseModel):
    """Payload for POST /submit_report."""
    centroid_id: int = Field(..., description="H3 hex cell being rated")
    user_id: str = Field(..., description="Supabase Auth UUID")
    rating_score: int = Field(..., ge=1, le=5, description="Safety rating 1-5")


class ReportOut(BaseModel):
    """Response / listing model for crowd reports."""
    report_id: int = 0
    centroid_id: int | None = None
    user_id: str | None = None
    rating_score: int | None = None
    timestamp: datetime | None = None
    is_verified: bool = False
    message: str | None = None
