"""
Router: /parse_news — NLP Hazard Scan Endpoint
================================================
Triggers the NLP pipeline to scrape news feeds, classify incidents,
and apply temporary M_news penalties to affected grid cells (DESIGN.md §2B).
"""

from fastapi import APIRouter

from app.schemas.news_schemas import NewsParseResponse

router = APIRouter()


@router.post("/parse_news", response_model=NewsParseResponse)
async def parse_news_hazards():
    """
    Trigger an on-demand scan of local news feeds.

    Pipeline:
    1. Fetch latest articles (models.nlp_hazard.scraper).
    2. Classify and extract entities (models.nlp_hazard.pipeline).
    3. Geocode incidents to H3 cells (models.nlp_hazard.geocoder).
    4. Upsert hazard records with expiry timers (data.crud.hazards).
    """
    # TODO: Wire to NLP pipeline
    return NewsParseResponse(
        status="not_implemented",
        hazards_detected=0,
        incidents=[],
    )
