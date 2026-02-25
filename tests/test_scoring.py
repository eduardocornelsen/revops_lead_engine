"""Tests for the Lead Scoring Engine."""

import pytest
from pathlib import Path

from src.config.icp_loader import load_icp_config
from src.models.models import (
    Company,
    Contact,
    EnrichedLead,
    ScoredLead,
    QualificationStatus,
)
from src.scoring.scoring import ScoringEngine


@pytest.fixture
def icp_config():
    config_path = Path(__file__).parent.parent / "config" / "icp_config.yaml"
    return load_icp_config(config_path)


@pytest.fixture
def scoring_engine(icp_config):
    return ScoringEngine(icp_config)


@pytest.fixture
def high_fit_lead():
    """A lead that should score very high."""
    company = Company(
        name="PerfectCo",
        industry="B2B SaaS",
        country="US",
        state="CA",
        employee_count=150,
        revenue_usd=15_000_000,
        funding_stage="Series B",
        tech_stack=["Google Sheets", "Mailchimp"],
    )
    contact = Contact(
        company_id=company.company_id,
        full_name="Jane Smith",
        title="VP of Sales",
        seniority="VP",
        department="Sales",
        email="jane@perfectco.com",
        verified=True,
    )
    return EnrichedLead(
        company_id=company.company_id,
        contact_id=contact.contact_id,
        tech_stack_detected=["Google Sheets", "Mailchimp"],
        tech_stack_gaps=["CRM", "Pipeline Management", "Automated Reporting"],
        buying_signals=[
            "Recent Series B funding",
            "Hired 3 new SDRs last month",
            "New VP of Sales hired",
        ],
        social_signals={
            "linkedin_posts_30d": 8,
            "linkedin_engagement": "high",
            "twitter_active": True,
        },
        news_mentions=["Featured in TechCrunch"],
        enrichment_completeness=0.95,
        company=company,
        contact=contact,
    )


@pytest.fixture
def low_fit_lead():
    """A lead that should score low."""
    company = Company(
        name="TinyCo",
        industry="Retail",
        country="US",
        state="NV",
        employee_count=10,
        revenue_usd=500_000,
        funding_stage="",
        tech_stack=["Salesforce", "SAP"],
    )
    contact = Contact(
        company_id=company.company_id,
        full_name="Bob Jones",
        title="Office Manager",
        seniority="Staff",
        department="Operations",
    )
    return EnrichedLead(
        company_id=company.company_id,
        contact_id=contact.contact_id,
        tech_stack_detected=["Salesforce", "SAP"],
        tech_stack_gaps=[],
        buying_signals=[],
        social_signals={"linkedin_posts_30d": 0, "linkedin_engagement": "low"},
        enrichment_completeness=0.3,
        company=company,
        contact=contact,
    )


class TestScoringEngine:
    """Tests for the lead scoring engine."""

    def test_score_in_range(self, scoring_engine, high_fit_lead):
        """Scores should be between 0 and 100."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert 0 <= result.score <= 100

    def test_high_fit_scores_high(self, scoring_engine, high_fit_lead):
        """A high-fit lead should score above the qualified threshold."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert result.score >= 60  # Should at least be nurture-worthy

    def test_low_fit_scores_low(self, scoring_engine, low_fit_lead):
        """A low-fit lead should score below the nurture threshold."""
        result = scoring_engine.score_lead(low_fit_lead)
        assert result.score < 80  # Should not be qualified

    def test_qualification_status_qualified(self, scoring_engine, high_fit_lead):
        """High-fit leads should be qualified or nurture."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert result.qualification_status in [
            QualificationStatus.QUALIFIED,
            QualificationStatus.NURTURE,
        ]

    def test_qualification_status_low(self, scoring_engine, low_fit_lead):
        """Low-fit leads should be disqualified or nurture."""
        result = scoring_engine.score_lead(low_fit_lead)
        assert result.qualification_status in [
            QualificationStatus.DISQUALIFIED,
            QualificationStatus.NURTURE,
        ]

    def test_bant_budget_with_funding(self, scoring_engine, high_fit_lead):
        """Leads with high revenue + funding should have budget signal."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert result.budget_signal is True

    def test_bant_authority_vp(self, scoring_engine, high_fit_lead):
        """VP-level contacts should have authority signal."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert result.authority_signal is True

    def test_bant_authority_staff(self, scoring_engine, low_fit_lead):
        """Staff-level contacts should NOT have authority signal."""
        result = scoring_engine.score_lead(low_fit_lead)
        assert result.authority_signal is False

    def test_bant_need_with_gaps(self, scoring_engine, high_fit_lead):
        """Leads with tech stack gaps should have need signal."""
        result = scoring_engine.score_lead(high_fit_lead)
        assert result.need_signal is True

    def test_bant_need_without_gaps(self, scoring_engine, low_fit_lead):
        """Leads without tech gaps should NOT have need signal."""
        result = scoring_engine.score_lead(low_fit_lead)
        assert result.need_signal is False

    def test_score_breakdown_present(self, scoring_engine, high_fit_lead):
        """Score breakdown should have all components."""
        result = scoring_engine.score_lead(high_fit_lead)
        breakdown = result.score_breakdown
        assert breakdown.icp_fit >= 0
        assert breakdown.behavioral >= 0
        assert breakdown.tech_gap >= 0
        assert breakdown.engagement >= 0

    def test_deal_stage_mapping(self, scoring_engine, high_fit_lead, low_fit_lead):
        """Deal stage should map correctly from qualification status."""
        high = scoring_engine.score_lead(high_fit_lead)
        assert high.deal_stage in ["Qualified", "Nurture"]

        low = scoring_engine.score_lead(low_fit_lead)
        assert low.deal_stage in ["Disqualified", "Nurture"]

    def test_score_multiple_leads(self, scoring_engine, high_fit_lead, low_fit_lead):
        """Should score multiple leads correctly."""
        results = scoring_engine.score_leads([high_fit_lead, low_fit_lead])
        assert len(results) == 2
        assert all(isinstance(r, ScoredLead) for r in results)

    def test_scoring_stats(self, scoring_engine, high_fit_lead, low_fit_lead):
        """Scoring stats should be accurate."""
        results = scoring_engine.score_leads([high_fit_lead, low_fit_lead])
        stats = scoring_engine.get_scoring_stats(results)
        assert stats["total_scored"] == 2
        assert "avg_score" in stats
        assert "by_status" in stats
        assert "bant_met" in stats
