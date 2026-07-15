"""
Router: /update_hazards — NLP Hazard Scan Endpoint
================================================
Triggers the NLP pipeline to scrape news feeds, classify incidents,
and apply temporary M_news penalties to affected grid cells (DESIGN.md §2B).
"""

import h3
from fastapi import APIRouter, Request
from geopy.geocoders import Nominatim

from app.schemas.news_schemas import NewsParseResponse
from models.nlp_hazard.scraper import fetch_all_feeds
from models.nlp_hazard.pipeline import load_pipeline, classify_article

router = APIRouter()

@router.post("/update_hazards", response_model=NewsParseResponse)
async def update_hazards(request: Request):
    """
    Trigger an on-demand scan of local news feeds.

    Pipeline:
    1. Fetch latest articles (models.nlp_hazard.scraper).
    2. Classify and extract entities (models.nlp_hazard.pipeline).
    3. Geocode incidents to H3 cells (geopy).
    4. Store active hazards in request.app.state.active_hazards.
    """
    articles = fetch_all_feeds()
    classifier, ner_pipeline = load_pipeline()
    geocoder = Nominatim(user_agent="NARI_Patna_App", timeout=5)
    
    if not hasattr(request.app.state, "active_hazards"):
        request.app.state.active_hazards = {}
        
    hazards_detected = 0
    incidents = []

    for article in articles:
        result = classify_article(article.title, classifier, ner_pipeline)
        if result is None:
            continue
            
        for loc in result.locations:
            try:
                geo = geocoder.geocode(f"{loc}, Patna, Bihar, India", exactly_one=True)
                if geo:
                    hex_id = h3.latlng_to_cell(geo.latitude, geo.longitude, 8)
                    request.app.state.active_hazards[hex_id] = max(
                        request.app.state.active_hazards.get(hex_id, 0.0),
                        result.severity
                    )
                    incidents.append({
                        "centroid_id": hex_id,
                        "description": result.headline,
                        "severity_score": result.severity,
                        "source_url": article.link
                    })
                    hazards_detected += 1
            except Exception as e:
                print(f"[NewsRouter] Failed to geocode {loc}: {e}")

    return NewsParseResponse(
        status="ok",
        hazards_detected=hazards_detected,
        incidents=incidents,
    )
