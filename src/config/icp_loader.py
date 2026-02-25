"""
B2B Lead Engine — ICP Configuration Loader

Loads and validates the ICP (Ideal Customer Profile) from YAML config.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


# ── ICP Pydantic Models ──────────────────────────────


class RevenueRange(BaseModel):
    min_usd: Optional[float] = None
    max_usd: Optional[float] = None
    min_brl: Optional[float] = None
    max_brl: Optional[float] = None


class EmployeeRange(BaseModel):
    min: int = 0
    max: int = 100_000


class Geography(BaseModel):
    countries: list[str] = []
    states: list[str] = []


class FirmographicFilters(BaseModel):
    industries: list[str] = []
    cnae_codes: list[str] = []
    revenue_range: RevenueRange = RevenueRange()
    employee_count: EmployeeRange = EmployeeRange()
    geography: Geography = Geography()
    company_type: list[str] = []
    funding_stage: list[str] = []


class TargetPersona(BaseModel):
    title: str
    seniority: str
    department: str


class TechStackSignals(BaseModel):
    positive_signals: list[str] = []
    negative_signals: list[str] = []


class BuyingSignals(BaseModel):
    high_intent: list[str] = []
    medium_intent: list[str] = []


class DataSource(BaseModel):
    provider: str
    priority: int = 1
    daily_limit: int = 100


class ICPProfile(BaseModel):
    name: str
    market: str
    enabled: bool = True
    firmographic_filters: FirmographicFilters = FirmographicFilters()
    target_personas: list[TargetPersona] = []
    tech_stack_signals: TechStackSignals = TechStackSignals()
    buying_signals: BuyingSignals = BuyingSignals()
    data_sources: list[DataSource] = []


class ScoringWeights(BaseModel):
    firmographic_fit: float = 0.30
    behavioral_signals: float = 0.25
    tech_stack_gap: float = 0.25
    engagement_signals: float = 0.20


class QualificationThresholds(BaseModel):
    qualified_min_score: float = 80
    nurture_min_score: float = 60
    disqualify_below: float = 60


class GlobalConfig(BaseModel):
    scoring_weights: ScoringWeights = ScoringWeights()
    qualification_thresholds: QualificationThresholds = QualificationThresholds()


class ICPConfig(BaseModel):
    version: str = "1.0"
    last_updated: str = ""
    global_config: GlobalConfig = Field(default_factory=GlobalConfig, alias="global")
    profiles: dict[str, ICPProfile] = {}

    model_config = {"populate_by_name": True}


# ── Loader ────────────────────────────────────────────


def load_icp_config(config_path: str | Path) -> ICPConfig:
    """
    Load and validate ICP configuration from a YAML file.

    Args:
        config_path: Path to the icp_config.yaml file

    Returns:
        Validated ICPConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config structure is invalid
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"ICP config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return ICPConfig(**raw)


def get_active_profiles(config: ICPConfig) -> list[ICPProfile]:
    """Return only enabled ICP profiles."""
    return [p for p in config.profiles.values() if p.enabled]


def get_profile_by_market(config: ICPConfig, market: str) -> Optional[ICPProfile]:
    """Get the first active profile matching a market code (e.g., 'US', 'BR')."""
    for profile in config.profiles.values():
        if profile.enabled and profile.market.upper() == market.upper():
            return profile
    return None
