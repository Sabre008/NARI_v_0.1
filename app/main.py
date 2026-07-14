"""
N.A.R.I — FastAPI Application Factory
======================================
Central entry point for the backend API. Registers all routers
and configures middleware (CORS, lifespan events).

Lifespan loads heavy assets (road graph, ML models) into memory
once at startup so they are shared across all requests.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import osmnx as ox
import pandas as pd
import h3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import routing, news, crowd, users
from models.safety_dnn.predict import SafetyPredictor
from routing.cost_function import compute_edge_safety, safety_to_cost
from services.demographic import get_demographic_multiplier

logger = logging.getLogger("nari")

# Paths relative to the project root (where uvicorn is launched)
GRAPH_PATH = Path("data") / "patna_road_graph.graphml"
FEATURES_PATH = Path("data") / "patna_h3_grid_features.csv"
ISOLATION_FOREST_PATH = Path("models") / "trust_engine" / "isolation_forest.joblib"
H3_RESOLUTION = 8

FEATURE_COLS = [
    "count_hospital", "count_police", "count_residential",
    "count_commercial", "count_hotel", "count_fire_station",
    "count_school", "count_bank", "count_bus_stop",
    "count_intersections",
]


def _build_node_safety_map(graph, hex_to_score: dict[str, float]) -> dict[int, float]:
    """Map every graph node to its H3 cell's S_infra score."""
    node_safety = {}
    for node_id, data in graph.nodes(data=True):
        cell = h3.latlng_to_cell(data["y"], data["x"], H3_RESOLUTION)
        node_safety[node_id] = hex_to_score.get(cell, 0.3)
    return node_safety


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Application lifespan handler.
    Startup: load road graph, DNN predictor, Isolation Forest, and
    pre-compute per-node S_infra scores.
    Shutdown: release references.
    """
    logger.info("N.A.R.I starting in %s mode", settings.NARI_ENV)

    # 1. Road graph
    if GRAPH_PATH.exists():
        application.state.graph = ox.load_graphml(str(GRAPH_PATH))
        logger.info(
            "Road graph loaded: %s nodes, %s edges",
            application.state.graph.number_of_nodes(),
            application.state.graph.number_of_edges(),
        )
    else:
        application.state.graph = None
        logger.warning("Road graph not found at %s", GRAPH_PATH)

    # 2. SafetyNet DNN predictor
    predictor = SafetyPredictor(
        input_dim=len(FEATURE_COLS),
        weights_path=settings.SAFETY_NET_WEIGHTS,
    )
    application.state.predictor = predictor
    logger.info("SafetyNet loaded (weights_found=%s)", predictor.is_loaded)

    # 3. H3 feature data and per-cell S_infra lookup
    if FEATURES_PATH.exists() and predictor.is_loaded:
        df_features = pd.read_csv(FEATURES_PATH)
        X = df_features[FEATURE_COLS].values.astype(np.float32)
        scores = predictor.predict(X)
        hex_to_score = dict(zip(df_features["hex_id"].values, scores))
        application.state.hex_to_score = hex_to_score
        logger.info("H3 feature data loaded: %d cells", len(hex_to_score))
    else:
        application.state.hex_to_score = {}
        logger.warning("H3 features or DNN weights missing; S_infra lookup disabled")

    # 4. Per-node safety map (pre-computed for routing)
    if application.state.graph is not None and application.state.hex_to_score:
        application.state.node_safety = _build_node_safety_map(
            application.state.graph, application.state.hex_to_score,
        )
        logger.info("Node safety map built: %d nodes", len(application.state.node_safety))
    else:
        application.state.node_safety = {}

    # 5. Isolation Forest (Trust Engine)
    if ISOLATION_FOREST_PATH.exists():
        application.state.trust_model = joblib.load(ISOLATION_FOREST_PATH)
        logger.info("Isolation Forest loaded from %s", ISOLATION_FOREST_PATH)
    else:
        application.state.trust_model = None
        logger.warning("Isolation Forest not found at %s", ISOLATION_FOREST_PATH)

    yield

    logger.info("N.A.R.I shutting down")


app = FastAPI(
    title="N.A.R.I — Navigation Aiding Reinforced Informatics",
    description="Infrastructure-aware safety navigation API for Patna, India.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routing.router, prefix="/api/v1", tags=["Routing"])
app.include_router(news.router, prefix="/api/v1", tags=["News & Hazards"])
app.include_router(crowd.router, prefix="/api/v1", tags=["Crowdsource"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])


@app.get("/health", tags=["System"])
async def health_check():
    """Liveness probe for deployment health checks."""
    graph_ok = app.state.graph is not None
    dnn_ok = app.state.predictor.is_loaded if hasattr(app.state, "predictor") else False
    trust_ok = app.state.trust_model is not None if hasattr(app.state, "trust_model") else False

    return {
        "status": "healthy" if graph_ok and dnn_ok else "degraded",
        "service": "nari-api",
        "version": "0.1.0",
        "components": {
            "road_graph": graph_ok,
            "safety_dnn": dnn_ok,
            "trust_engine": trust_ok,
        },
    }
