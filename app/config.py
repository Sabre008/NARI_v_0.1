"""
N.A.R.I — Application Configuration
=====================================
Centralised settings loaded from environment variables / .env file.
Uses Pydantic Settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configurable parameters for the N.A.R.I backend.
    Values are read from environment variables or a `.env` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Supabase ────────────────────────────────────────
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_KEY: str = "placeholder-key"

    # ── Application ─────────────────────────────────────
    NARI_ENV: str = "development"
    NARI_LOG_LEVEL: str = "INFO"

    # ── FastAPI ─────────────────────────────────────────
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000

    # ── Model Paths ─────────────────────────────────────
    SAFETY_NET_WEIGHTS: str = "models/safety_dnn/weights/safety_net.pth"

    # ── Routing Defaults ────────────────────────────────
    MAX_DETOUR_FACTOR: float = 1.25  # §3 constraint: 1.25× shortest distance
    K_SHORTEST_PATHS: int = 5        # Number of candidate paths for Yen's KSP

    # ── Trust Engine ────────────────────────────────────
    DECAY_LAMBDA: float = 0.05       # λ for W_report = Rating · e^(−λt)

    # ── Scoring Weights ─────────────────────────────────
    ALPHA_CROWD: float = 0.3         # α weight for Crowd_decay in S_total
    BETA_NEWS: float = 0.2           # β weight for News_severity in S_total


# Singleton instance — import `settings` from this module everywhere.
settings = Settings()
