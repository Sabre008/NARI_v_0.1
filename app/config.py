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

    # ── API Base Override (Optional) ────────────────────
    API_URL: str = ""
    API_BASE: str = ""

    def get_api_url(self) -> str:
        """
        Dynamically and securely resolve the backend API base URL:
        1. Explicit configuration or environment variables (API_URL, API_BASE, NARI_API_URL).
        2. Streamlit secrets (if running in a Streamlit context).
        3. GitHub Codespaces runtime detection (CODESPACE_NAME + port forwarding domain).
        4. Standard local development fallback (http://127.0.0.1:{FASTAPI_PORT}).
        """
        import os

        env_url = (
            self.API_URL
            or self.API_BASE
            or os.getenv("API_URL")
            or os.getenv("API_BASE")
            or os.getenv("NARI_API_URL")
        )
        if env_url:
            return env_url.rstrip("/").removesuffix("/api/v1")

        try:
            import streamlit as st
            if hasattr(st, "secrets") and "API_URL" in st.secrets:
                return str(st.secrets["API_URL"]).rstrip("/").removesuffix("/api/v1")
        except Exception:
            pass

        codespace_name = os.getenv("CODESPACE_NAME")
        if codespace_name:
            domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
            return f"https://{codespace_name}-{self.FASTAPI_PORT}.{domain}"

        return f"http://127.0.0.1:{self.FASTAPI_PORT}"

    def get_route_url(self) -> str:
        """Fully-qualified safe routing endpoint URL."""
        return f"{self.get_api_url()}/api/v1/route"

    def get_health_url(self) -> str:
        """Fully-qualified health probe endpoint URL."""
        return f"{self.get_api_url()}/health"

    def get_environment_label(self) -> str:
        """Human-readable badge for UI status display."""
        import os
        if os.getenv("CODESPACE_NAME"):
            return f"GitHub Codespace ({os.getenv('CODESPACE_NAME')})"
        return "Localhost Development"

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


# ── Module-level convenience wrappers ──────────────────────
def get_api_url() -> str:
    """Return the dynamically resolved API base URL."""
    return settings.get_api_url()


def get_route_url() -> str:
    """Return the fully-qualified safe routing endpoint URL."""
    return settings.get_route_url()


def get_health_url() -> str:
    """Return the fully-qualified health check endpoint URL."""
    return settings.get_health_url()


def get_environment_label() -> str:
    """Return the active environment label."""
    return settings.get_environment_label()

