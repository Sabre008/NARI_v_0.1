"""
N.A.R.I — FastAPI Application Factory
======================================
Central entry point for the backend API. Registers all routers
and configures middleware (CORS, lifespan events).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import routing, news, crowd, users


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Application lifespan handler.
    - **Startup**: Load ML models, warm caches, connect to Supabase.
    - **Shutdown**: Release resources gracefully.
    """
    # ── Startup ──────────────────────────────────────────
    # TODO: Load SafetyNet weights, build road graph, init Supabase client
    print(f"[N.A.R.I] Starting in {settings.NARI_ENV} mode")
    yield
    # ── Shutdown ─────────────────────────────────────────
    print("[N.A.R.I] Shutting down gracefully")


app = FastAPI(
    title="N.A.R.I — Navigation Aiding Reinforced Informatics",
    description="Infrastructure-aware safety navigation API for Patna, India.",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS (allow Streamlit frontend to call the API) ─────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────
app.include_router(routing.router, prefix="/api/v1", tags=["Routing"])
app.include_router(news.router, prefix="/api/v1", tags=["News & Hazards"])
app.include_router(crowd.router, prefix="/api/v1", tags=["Crowdsource"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])


@app.get("/health", tags=["System"])
async def health_check():
    """Liveness probe for deployment health checks."""
    return {"status": "healthy", "service": "nari-api", "version": "0.1.0"}
