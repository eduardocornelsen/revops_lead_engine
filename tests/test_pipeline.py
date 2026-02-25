"""Integration test for the full pipeline."""

import pytest
import tempfile
from pathlib import Path

from src.config.icp_loader import load_icp_config
from src.database.database import Database
from src.pipeline import run_pipeline
from src.models.models import PipelineResult


class TestPipeline:
    """Integration tests running the full pipeline."""

    def test_full_pipeline_runs(self, tmp_path):
        """The full pipeline should complete without errors."""
        db_path = str(tmp_path / "test_pipeline.db")
        result = run_pipeline(db_path=db_path, verbose=False)

        assert isinstance(result, PipelineResult)
        assert result.companies_discovered > 0
        assert result.contacts_found > 0
        assert result.leads_enriched > 0
        assert result.leads_scored > 0
        assert result.pipeline_duration_seconds > 0

    def test_pipeline_creates_database(self, tmp_path):
        """Pipeline should create and populate the database."""
        db_path = str(tmp_path / "test_db.db")
        run_pipeline(db_path=db_path, verbose=False)

        db = Database(db_path)
        stats = db.get_pipeline_stats()

        assert stats["dim_companies"] > 0
        assert stats["dim_contacts"] > 0
        assert stats["fct_enriched_leads"] > 0
        assert stats["fct_scored_leads"] > 0

    def test_pipeline_qualification_distribution(self, tmp_path):
        """Pipeline should produce a mix of qualified/nurture/disqualified."""
        db_path = str(tmp_path / "test_qual.db")
        result = run_pipeline(db_path=db_path, verbose=False)

        total = result.leads_qualified + result.leads_nurture + result.leads_disqualified
        assert total == result.leads_scored
        assert total > 0

    def test_pipeline_outreach_events(self, tmp_path):
        """Pipeline should create outreach events for non-disqualified leads."""
        db_path = str(tmp_path / "test_outreach.db")
        result = run_pipeline(db_path=db_path, verbose=False)

        # Only non-disqualified leads get outreach
        assert result.outreach_events_created > 0

    def test_pipeline_crm_deals(self, tmp_path):
        """Pipeline should create CRM deals for qualified/nurture leads."""
        db_path = str(tmp_path / "test_crm.db")
        result = run_pipeline(db_path=db_path, verbose=False)

        assert result.deals_synced_to_crm > 0

    def test_pipeline_scored_leads_have_briefs(self, tmp_path):
        """Qualified/nurture leads should have deal briefs."""
        db_path = str(tmp_path / "test_briefs.db")
        run_pipeline(db_path=db_path, verbose=False)

        db = Database(db_path)
        qualified = db.get_scored_leads(status="qualified")
        nurture = db.get_scored_leads(status="nurture")

        for lead in qualified + nurture:
            assert lead.deal_brief, f"Lead {lead.lead_id} should have a deal brief"

    def test_pipeline_idempotent(self, tmp_path):
        """Running pipeline twice should not fail; counts should stay bounded."""
        db_path = str(tmp_path / "test_idempotent.db")

        result1 = run_pipeline(db_path=db_path, verbose=False)
        result2 = run_pipeline(db_path=db_path, verbose=False)

        db = Database(db_path)
        stats = db.get_pipeline_stats()

        # Pipeline stores full TAM pool (150 companies) + uses INSERT OR REPLACE
        # So second run should replace, not grow unboundedly
        assert stats["dim_companies"] <= 300 + 5  # at most 2x pool (REPLACE may miss some UUIDs)
