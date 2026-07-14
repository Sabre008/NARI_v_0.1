"""
Router: /submit_report & /reports — Crowdsource Endpoints
==========================================================
Handles user safety reports. Submissions are validated through the
Isolation Forest trust engine before influencing scores (DESIGN.md §2C).
"""

from fastapi import APIRouter

from app.schemas.crowd_schemas import ReportSubmission, ReportOut

router = APIRouter()


@router.post("/submit_report", response_model=ReportOut)
async def submit_report(payload: ReportSubmission):
    """
    Submit a crowdsourced safety report for a grid cell.

    Pipeline:
    1. Validate user identity and rate-limit (app.dependencies).
    2. Run Isolation Forest anomaly check (models.trust_engine).
    3. If verified, insert into crowd_reports (data.crud.reports).
    4. Return verification status and applied weight.
    """
    # TODO: Wire to trust engine + data layer
    return ReportOut(
        report_id=0,
        is_verified=False,
        message="Report submission not yet wired.",
    )


@router.get("/reports/{centroid_id}", response_model=list[ReportOut])
async def get_reports(centroid_id: int):
    """
    Retrieve all verified crowd reports for a specific grid cell.
    Results are sorted by timestamp (newest first).
    """
    # TODO: Wire to data.crud.reports
    return []
