"""Tests for ICP configuration loader."""

import pytest
from pathlib import Path

from src.config.icp_loader import (
    load_icp_config,
    get_active_profiles,
    get_profile_by_market,
    ICPConfig,
)


@pytest.fixture
def icp_config():
    """Load the project's ICP config."""
    config_path = Path(__file__).parent.parent / "config" / "icp_config.yaml"
    return load_icp_config(config_path)


class TestICPLoader:
    """Tests for ICP YAML config loading and validation."""

    def test_load_config_success(self, icp_config):
        """Config should load and parse successfully."""
        assert isinstance(icp_config, ICPConfig)
        assert icp_config.version == "1.0"

    def test_config_has_profiles(self, icp_config):
        """Config should contain at least one profile."""
        assert len(icp_config.profiles) >= 2

    def test_us_profile_exists(self, icp_config):
        """US B2B SaaS profile should be present."""
        assert "us_b2b_saas" in icp_config.profiles
        us = icp_config.profiles["us_b2b_saas"]
        assert us.market == "US"
        assert us.enabled is True

    def test_brazil_profile_exists(self, icp_config):
        """Brazil tech profile should be present."""
        assert "brazil_tech" in icp_config.profiles
        br = icp_config.profiles["brazil_tech"]
        assert br.market == "BR"
        assert br.enabled is True

    def test_firmographic_filters(self, icp_config):
        """US profile should have valid firmographic filters."""
        us = icp_config.profiles["us_b2b_saas"]
        filters = us.firmographic_filters

        assert len(filters.industries) > 0
        assert "B2B SaaS" in filters.industries
        assert filters.revenue_range.min_usd == 2_000_000
        assert filters.employee_count.min == 50
        assert "US" in filters.geography.countries

    def test_target_personas(self, icp_config):
        """US profile should have target personas."""
        us = icp_config.profiles["us_b2b_saas"]
        assert len(us.target_personas) >= 3
        titles = [p.title for p in us.target_personas]
        assert "VP of Sales" in titles

    def test_scoring_weights(self, icp_config):
        """Global scoring weights should sum to 1.0."""
        weights = icp_config.global_config.scoring_weights
        total = (
            weights.firmographic_fit
            + weights.behavioral_signals
            + weights.tech_stack_gap
            + weights.engagement_signals
        )
        assert abs(total - 1.0) < 0.01

    def test_get_active_profiles(self, icp_config):
        """Should return only enabled profiles."""
        active = get_active_profiles(icp_config)
        assert len(active) >= 2
        assert all(p.enabled for p in active)

    def test_get_profile_by_market(self, icp_config):
        """Should find profiles by market code."""
        us = get_profile_by_market(icp_config, "US")
        assert us is not None
        assert us.market == "US"

        br = get_profile_by_market(icp_config, "BR")
        assert br is not None
        assert br.market == "BR"

        # Non-existent market
        none_profile = get_profile_by_market(icp_config, "JP")
        assert none_profile is None

    def test_load_nonexistent_config(self):
        """Should raise FileNotFoundError for missing config."""
        with pytest.raises(FileNotFoundError):
            load_icp_config("/nonexistent/path.yaml")

    def test_brazil_cnae_codes(self, icp_config):
        """Brazil profile should have CNAE codes."""
        br = icp_config.profiles["brazil_tech"]
        assert len(br.firmographic_filters.cnae_codes) > 0
        assert "6201-5" in br.firmographic_filters.cnae_codes
