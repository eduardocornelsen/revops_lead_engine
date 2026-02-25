"""
B2B Lead Engine — Stage 2: Enrichment Pipeline

Enriches discovered leads with tech stack, buying signals,
social signals, and news mentions from multiple providers.

MVP uses mock enrichment; interface ready for real API swap-in.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from src.models.models import Company, Contact, EnrichedLead


# ── Mock Enrichment Data ──────────────────────────────

TECH_STACKS = {
    "crm": ["Salesforce", "HubSpot", "Pipedrive", "Zoho CRM", "None detected"],
    "analytics": ["Tableau", "Looker", "Power BI", "Google Analytics", "None detected"],
    "marketing": ["Marketo", "Mailchimp", "RD Station", "ActiveCampaign", "None detected"],
    "data": ["Snowflake", "BigQuery", "Redshift", "PostgreSQL", "Google Sheets"],
    "automation": ["Zapier", "n8n", "Make", "None detected"],
}

TECH_GAPS_MAP = {
    "None detected": ["CRM", "Pipeline Management"],
    "Google Sheets": ["CRM", "Automated Reporting"],
    "Excel": ["CRM", "Real-time Analytics"],
    "Planilhas": ["CRM", "Dashboard"],
}

BUYING_SIGNALS_POOL = [
    "Recent Series funding round",
    "Hired 3 new SDRs last month",
    "New VP of Sales hired",
    "Expanding to new market",
    "Job posting for RevOps role",
    "Product launch announced",
    "Competitor partnership lost",
    "Revenue growth >30% YoY",
    "Board member change",
    "New CRO appointment",
]

NEWS_POOL = [
    "Company featured in TechCrunch for rapid growth",
    "Announced expansion to Latin American markets",
    "Named in Forbes 'Companies to Watch' list",
    "Launched new enterprise product tier",
    "Partnership with major cloud provider announced",
    "Opened new office in growth market",
]


class EnrichmentPipeline:
    """
    Multi-source enrichment pipeline.

    In MVP, simulates enrichment from Apollo, Hunter, BuiltWith,
    and Google News. In production, each provider is a real API client.
    """

    def __init__(self):
        self.providers = ["apollo_mock", "hunter_mock", "builtwith_mock", "news_mock"]

    def enrich(
        self, companies: list[Company], contacts: list[Contact]
    ) -> list[EnrichedLead]:
        """
        Enrich all company-contact pairs into unified lead records.

        Args:
            companies: Discovered companies
            contacts: Discovered contacts

        Returns:
            List of enriched leads
        """
        # Build company lookup
        company_map = {c.company_id: c for c in companies}

        enriched_leads = []
        for contact in contacts:
            company = company_map.get(contact.company_id)
            if not company:
                continue

            lead = self._enrich_lead(company, contact)
            enriched_leads.append(lead)

        return enriched_leads

    def _enrich_lead(self, company: Company, contact: Contact) -> EnrichedLead:
        """Enrich a single company-contact pair."""

        # Simulate tech stack detection (BuiltWith mock)
        tech_detected = list(company.tech_stack)  # Start with known tech
        for category, tools in TECH_STACKS.items():
            if not any(t in tech_detected for t in tools):
                tech_detected.append(random.choice(tools))

        # Identify tech gaps
        tech_gaps = []
        for tech in tech_detected:
            if tech in TECH_GAPS_MAP:
                tech_gaps.extend(TECH_GAPS_MAP[tech])
        tech_gaps = list(set(tech_gaps))

        # Simulate buying signals
        num_signals = random.randint(1, 4)
        buying_signals = random.sample(
            BUYING_SIGNALS_POOL, min(num_signals, len(BUYING_SIGNALS_POOL))
        )

        # Add funding-specific signal if funded
        if company.funding_stage and "Series" in company.funding_stage:
            buying_signals.append(
                f"Recent {company.funding_stage} funding"
            )

        # Simulate social signals
        social_signals = {
            "linkedin_posts_30d": random.randint(0, 15),
            "linkedin_engagement": random.choice(["low", "medium", "high"]),
            "twitter_active": random.choice([True, False]),
            "content_themes": random.sample(
                ["sales", "growth", "hiring", "product", "fundraising", "culture"],
                k=random.randint(1, 3),
            ),
        }

        # Simulate news mentions
        num_news = random.randint(0, 2)
        news_mentions = random.sample(NEWS_POOL, min(num_news, len(NEWS_POOL)))

        # Calculate enrichment completeness
        fields_filled = sum([
            bool(tech_detected),
            bool(tech_gaps),
            bool(buying_signals),
            bool(social_signals.get("linkedin_posts_30d", 0) > 0),
            bool(news_mentions),
            bool(contact.email),
            bool(contact.verified),
        ])
        completeness = round(fields_filled / 7.0, 2)

        return EnrichedLead(
            company_id=company.company_id,
            contact_id=contact.contact_id,
            tech_stack_detected=tech_detected,
            tech_stack_gaps=tech_gaps,
            buying_signals=buying_signals,
            social_signals=social_signals,
            news_mentions=news_mentions,
            enrichment_completeness=completeness,
            enrichment_sources=self.providers,
            company=company,
            contact=contact,
        )

    def get_enrichment_stats(self, leads: list[EnrichedLead]) -> dict:
        """Generate enrichment statistics."""
        avg_completeness = (
            sum(l.enrichment_completeness for l in leads) / len(leads)
            if leads else 0
        )

        has_gaps = sum(1 for l in leads if l.tech_stack_gaps)
        has_buying = sum(1 for l in leads if l.buying_signals)
        has_news = sum(1 for l in leads if l.news_mentions)

        return {
            "total_enriched": len(leads),
            "avg_completeness": round(avg_completeness, 2),
            "leads_with_tech_gaps": has_gaps,
            "leads_with_buying_signals": has_buying,
            "leads_with_news": has_news,
            "sources_used": self.providers,
        }
