"""
B2B Lead Engine — Pydantic Data Models

Core domain models used across all pipeline stages.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _uuid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ─────────────────────────────────────────────


class QualificationStatus(str, Enum):
    QUALIFIED = "qualified"
    NURTURE = "nurture"
    DISQUALIFIED = "disqualified"


class OutreachChannel(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"


class OutreachStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"


class ResponseType(str, Enum):
    INTERESTED = "interested"
    NOT_NOW = "not_now"
    NOT_INTERESTED = "not_interested"
    OUT_OF_OFFICE = "ooo"
    AUTO_REPLY = "auto_reply"


# ── Core Models ───────────────────────────────────────


class Company(BaseModel):
    """A discovered target company."""

    company_id: str = Field(default_factory=lambda: _uuid("c"))
    name: str
    industry: str = ""
    country: str = ""
    state: str = ""
    employee_count: int = 0
    revenue_usd: float = 0.0
    website: str = ""
    tech_stack: list[str] = []
    funding_stage: str = ""
    founded_year: Optional[int] = None
    cnpj: Optional[str] = None
    cnae_code: Optional[str] = None
    source: str = "manual"
    discovered_at: datetime = Field(default_factory=_now)

    @property
    def tech_stack_json(self) -> str:
        return json.dumps(self.tech_stack)


class Contact(BaseModel):
    """A decision-maker contact at a company."""

    contact_id: str = Field(default_factory=lambda: _uuid("ct"))
    company_id: str
    full_name: str
    title: str = ""
    email: str = ""
    phone: str = ""
    linkedin_url: str = ""
    seniority: str = ""
    department: str = ""
    source: str = "manual"
    verified: bool = False
    discovered_at: datetime = Field(default_factory=_now)


class EnrichedLead(BaseModel):
    """A lead enriched with multi-source signals."""

    lead_id: str = Field(default_factory=lambda: _uuid("l"))
    company_id: str
    contact_id: str
    tech_stack_detected: list[str] = []
    tech_stack_gaps: list[str] = []
    buying_signals: list[str] = []
    social_signals: dict = {}
    news_mentions: list[str] = []
    enrichment_completeness: float = 0.0
    enrichment_sources: list[str] = []
    enriched_at: datetime = Field(default_factory=_now)

    # Denormalized for convenience (populated during pipeline)
    company: Optional[Company] = None
    contact: Optional[Contact] = None


class ScoreBreakdown(BaseModel):
    """Breakdown of how a lead score was computed."""

    icp_fit: float = 0.0
    behavioral: float = 0.0
    tech_gap: float = 0.0
    engagement: float = 0.0
    reasons: list[str] = Field(default_factory=list)


class ScoredLead(BaseModel):
    """A scored and qualified lead with deal brief."""

    lead_id: str
    score: float = 0.0
    score_breakdown: ScoreBreakdown = ScoreBreakdown()
    qualification_status: QualificationStatus = QualificationStatus.DISQUALIFIED
    budget_signal: bool = False
    authority_signal: bool = False
    need_signal: bool = False
    timeline_signal: bool = False
    deal_brief: str = ""
    deal_stage: str = ""
    scored_at: datetime = Field(default_factory=_now)

    # Denormalized
    enriched_lead: Optional[EnrichedLead] = None


class OutreachEvent(BaseModel):
    """A single outreach interaction."""

    event_id: str = Field(default_factory=lambda: _uuid("e"))
    lead_id: str
    channel: OutreachChannel = OutreachChannel.EMAIL
    sequence_step: int = 1
    subject: str = ""
    body: str = ""
    status: OutreachStatus = OutreachStatus.PENDING
    response_type: Optional[ResponseType] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None


class DealBrief(BaseModel):
    """AI-generated deal brief for a qualified lead."""

    lead_id: str
    company_name: str
    company_summary: str = ""
    contact_name: str = ""
    contact_title: str = ""
    bant_summary: dict = {}
    spin_questions: list[dict] = []
    objection_handling: list[dict] = []
    call_script: str = ""
    generated_at: datetime = Field(default_factory=_now)

    def to_text(self) -> str:
        """Render deal brief as formatted text."""
        lines = [
            "═" * 55,
            f"DEAL BRIEF: {self.company_name}",
            "═" * 55,
            "",
            f"COMPANY: {self.company_summary}",
            f"CONTACT: {self.contact_name}, {self.contact_title}",
            "",
            "BANT QUALIFICATION:",
        ]

        for key, val in self.bant_summary.items():
            icon = "✅" if val.get("met", False) else "⚠️"
            lines.append(f"  {icon} {key}: {val.get('detail', 'N/A')}")

        lines.append("")
        lines.append("SPIN DISCOVERY QUESTIONS:")
        for q in self.spin_questions:
            lines.append(f'  [{q.get("type", "?")}] "{q.get("question", "")}"')

        lines.append("")
        lines.append("OBJECTION PREP:")
        for obj in self.objection_handling:
            lines.append(f'  • "{obj.get("objection", "")}" → "{obj.get("response", "")}"')

        lines.append("═" * 55)
        return "\n".join(lines)


class PipelineResult(BaseModel):
    """Result summary from running the full pipeline."""

    companies_discovered: int = 0
    contacts_found: int = 0
    leads_enriched: int = 0
    leads_scored: int = 0
    leads_qualified: int = 0
    leads_nurture: int = 0
    leads_disqualified: int = 0
    outreach_events_created: int = 0
    deals_synced_to_crm: int = 0
    pipeline_duration_seconds: float = 0.0
    completed_at: datetime = Field(default_factory=_now)
