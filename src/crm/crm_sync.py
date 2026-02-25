"""
B2B Lead Engine — Stage 5: CRM Sync & Handoff

Mock HubSpot CRM client with deal creation, stage mapping,
and attribution tagging.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.models.models import (
    ScoredLead,
    OutreachEvent,
    QualificationStatus,
)


class CRMDeal:
    """Represents a deal in the CRM system."""

    def __init__(
        self,
        deal_id: str,
        company_name: str,
        contact_name: str,
        deal_stage: str,
        amount: float,
        lead_score: float,
        lead_source: str,
        enrichment_sources: list[str],
        outreach_channel: str,
        attribution: dict,
        created_at: datetime,
    ):
        self.deal_id = deal_id
        self.company_name = company_name
        self.contact_name = contact_name
        self.deal_stage = deal_stage
        self.amount = amount
        self.lead_score = lead_score
        self.lead_source = lead_source
        self.enrichment_sources = enrichment_sources
        self.outreach_channel = outreach_channel
        self.attribution = attribution
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "deal_id": self.deal_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "deal_stage": self.deal_stage,
            "amount": self.amount,
            "lead_score": self.lead_score,
            "lead_source": self.lead_source,
            "enrichment_sources": self.enrichment_sources,
            "outreach_channel": self.outreach_channel,
            "attribution": self.attribution,
            "created_at": self.created_at.isoformat(),
        }


class CRMSync:
    """
    Mock HubSpot CRM sync client.

    Creates deals from scored leads, maps stages,
    tags attribution, and tracks sync status.

    In production, this would use the HubSpot/Salesforce API.
    """

    # ── Deal Stage Mapping ────────────────────────────
    STAGE_MAP = {
        QualificationStatus.QUALIFIED: "Qualified Lead",
        QualificationStatus.NURTURE: "Nurture Sequence",
        QualificationStatus.DISQUALIFIED: "Disqualified",
    }

    # ── Deal Amount Estimation ────────────────────────
    AMOUNT_MULTIPLIERS = {
        QualificationStatus.QUALIFIED: 0.10,     # 10% of company revenue
        QualificationStatus.NURTURE: 0.05,       # 5% of company revenue
        QualificationStatus.DISQUALIFIED: 0.0,
    }

    def __init__(self):
        self.deals: list[CRMDeal] = []
        self.sync_log: list[dict] = []

    def sync_leads(
        self,
        scored_leads: list[ScoredLead],
        outreach_events: list[OutreachEvent],
    ) -> list[CRMDeal]:
        """
        Sync scored leads to CRM as deals.

        Only syncs qualified and nurture leads.
        """
        # Build outreach lookup
        outreach_by_lead = {}
        for event in outreach_events:
            if event.lead_id not in outreach_by_lead:
                outreach_by_lead[event.lead_id] = []
            outreach_by_lead[event.lead_id].append(event)

        for lead in scored_leads:
            if lead.qualification_status == QualificationStatus.DISQUALIFIED:
                continue

            enriched = lead.enriched_lead
            if not enriched or not enriched.company or not enriched.contact:
                continue

            company = enriched.company
            contact = enriched.contact

            # Build attribution data
            lead_events = outreach_by_lead.get(lead.lead_id, [])
            converting_channel = "email"
            converting_step = 0
            for event in lead_events:
                if event.response_type and event.response_type.value == "interested":
                    converting_channel = event.channel.value
                    converting_step = event.sequence_step
                    break

            attribution = {
                "lead_source": company.source,
                "enrichment_sources": enriched.enrichment_sources,
                "outreach_channel": converting_channel,
                "converting_step": converting_step,
                "lead_score": lead.score,
                "bant_met": sum([
                    lead.budget_signal,
                    lead.authority_signal,
                    lead.need_signal,
                    lead.timeline_signal,
                ]),
            }

            # Estimate deal amount
            multiplier = self.AMOUNT_MULTIPLIERS.get(
                lead.qualification_status, 0.0
            )
            amount = company.revenue_usd * multiplier

            deal = CRMDeal(
                deal_id=f"deal-{uuid4().hex[:8]}",
                company_name=company.name,
                contact_name=contact.full_name,
                deal_stage=self.STAGE_MAP.get(
                    lead.qualification_status, "Unknown"
                ),
                amount=round(amount, 2),
                lead_score=lead.score,
                lead_source=company.source,
                enrichment_sources=enriched.enrichment_sources,
                outreach_channel=converting_channel,
                attribution=attribution,
                created_at=datetime.now(timezone.utc),
            )

            self.deals.append(deal)
            self.sync_log.append({
                "action": "deal_created",
                "deal_id": deal.deal_id,
                "company": company.name,
                "stage": deal.deal_stage,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        return self.deals

    def get_sync_stats(self) -> dict:
        """Generate CRM sync statistics."""
        if not self.deals:
            return {"total_deals": 0}

        by_stage = {}
        total_pipeline = 0.0
        for deal in self.deals:
            by_stage[deal.deal_stage] = by_stage.get(deal.deal_stage, 0) + 1
            total_pipeline += deal.amount

        return {
            "total_deals": len(self.deals),
            "by_stage": by_stage,
            "total_pipeline_value": round(total_pipeline, 2),
            "avg_deal_size": round(total_pipeline / len(self.deals), 2),
            "sync_events": len(self.sync_log),
        }
