"""
B2B Lead Engine — Application Settings

Central configuration using Pydantic BaseSettings.
Environment variables override defaults (use .env file or export).
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # ── Database ──────────────────────────────────────
    database_path: str = Field(
        default=str(PROJECT_ROOT / "data" / "lead_engine.db"),
        description="Path to SQLite database file",
    )

    # ── ICP Config ────────────────────────────────────
    icp_config_path: str = Field(
        default=str(PROJECT_ROOT / "config" / "icp_config.yaml"),
        description="Path to ICP configuration YAML",
    )

    # ── API Keys (optional — mock providers used if empty) ──
    apollo_api_key: str = Field(default="", description="Apollo.io API key")
    hunter_api_key: str = Field(default="", description="Hunter.io API key")
    builtwith_api_key: str = Field(default="", description="BuiltWith API key")
    openai_api_key: str = Field(default="", description="OpenAI API key for deal briefs")

    # ── API Server ────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="FastAPI host")
    api_port: int = Field(default=8000, description="FastAPI port")

    # ── Scoring ───────────────────────────────────────
    qualified_min_score: float = Field(default=80.0)
    nurture_min_score: float = Field(default=60.0)

    # ── Outreach ──────────────────────────────────────
    outreach_sequence_days: list[int] = Field(
        default=[1, 3, 7],
        description="Days between outreach touches",
    )

    model_config = {
        "env_prefix": "LEAD_ENGINE_",
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
