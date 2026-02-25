"""
B2B Lead Engine — Stage 1: Lead Discovery Engine

Discovers companies matching ICP filters from data providers.
MVP uses mock data; interface supports real API integrations.
"""

from __future__ import annotations

from src.config.icp_loader import ICPConfig, ICPProfile, get_active_profiles
from src.models.models import Company, Contact
from src.database.seed_data import generate_seed_companies, generate_seed_contacts


class DiscoveryEngine:
    """
    Lead discovery engine that filters companies against ICP criteria.

    In MVP mode, uses seed data. In production, queries Apollo.io,
    Receita Federal, Crunchbase, etc.
    """

    def __init__(self, icp_config: ICPConfig):
        self.icp_config = icp_config
        self.active_profiles = get_active_profiles(icp_config)

    def discover(
        self,
        companies: list[Company] | None = None,
        contacts: list[Contact] | None = None,
    ) -> tuple[list[Company], list[Contact]]:
        """
        Run discovery pipeline.

        Args:
            companies: Pre-generated companies to filter. If None, generates seed data.
            contacts: Pre-generated contacts to filter. If None, generates from companies.

        Returns:
            Tuple of (discovered companies, discovered contacts)
        """
        if companies is None:
            companies = generate_seed_companies()
        if contacts is None:
            contacts = generate_seed_contacts(companies)

        # Filter companies against active ICP profiles
        matched_companies = []
        for company in companies:
            for profile in self.active_profiles:
                if self._matches_icp(company, profile):
                    matched_companies.append(company)
                    break

        # Keep only contacts for matched companies
        matched_ids = {c.company_id for c in matched_companies}
        matched_contacts = [c for c in contacts if c.company_id in matched_ids]

        return matched_companies, matched_contacts

    def _matches_icp(self, company: Company, profile: ICPProfile) -> bool:
        """Check if a company matches an ICP profile's filters."""
        filters = profile.firmographic_filters

        # Market/country check
        geo = filters.geography
        if geo.countries and company.country not in geo.countries:
            return False

        # State check (if specified)
        if geo.states and company.state and company.state not in geo.states:
            return False

        # Industry check
        if filters.industries and company.industry not in filters.industries:
            return False

        # Employee count check
        emp = filters.employee_count
        if company.employee_count < emp.min or company.employee_count > emp.max:
            return False

        # Revenue check (handle USD and BRL)
        rev = filters.revenue_range
        if rev.min_usd and company.revenue_usd < rev.min_usd:
            return False
        if rev.max_usd and company.revenue_usd > rev.max_usd:
            return False
        if rev.min_brl and company.revenue_usd < rev.min_brl:
            return False
        if rev.max_brl and company.revenue_usd > rev.max_brl:
            return False

        # Funding stage check
        if filters.funding_stage and company.funding_stage:
            if company.funding_stage not in filters.funding_stage:
                return False

        return True

    def get_discovery_stats(
        self, companies: list[Company], contacts: list[Contact]
    ) -> dict:
        """Generate discovery statistics."""
        by_country = {}
        by_industry = {}

        for c in companies:
            by_country[c.country] = by_country.get(c.country, 0) + 1
            by_industry[c.industry] = by_industry.get(c.industry, 0) + 1

        return {
            "total_companies": len(companies),
            "total_contacts": len(contacts),
            "by_country": by_country,
            "by_industry": by_industry,
            "profiles_used": [p.name for p in self.active_profiles],
        }
