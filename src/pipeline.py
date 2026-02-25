"""
B2B Lead Engine — End-to-End Pipeline Orchestrator

Runs all 5 stages in sequence with progress tracking and stats output.
Produces a progressively decreasing funnel tracked at the company level.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

from src.config.settings import settings
from src.config.icp_loader import load_icp_config
from src.database.database import Database
from src.database.seed_data import generate_seed_companies, generate_seed_contacts
from src.discovery.discovery import DiscoveryEngine
from src.enrichment.enrichment import EnrichmentPipeline
from src.scoring.scoring import ScoringEngine
from src.scoring.deal_brief import DealBriefGenerator
from src.outreach.outreach import OutreachEngine
from src.crm.crm_sync import CRMSync
from src.models.models import PipelineResult


# ── Console Formatting ────────────────────────────────

BOLD = "\033[1m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "✅"
ROCKET = "🚀"
CHART = "📊"
MAIL = "📧"
LINK = "🔗"
WARN = "⚠️"


def _header(stage: int, title: str):
    print(f"\n{'═' * 60}")
    print(f"{BOLD}{BLUE}  STAGE {stage}: {title}{RESET}")
    print(f"{'═' * 60}")


def _stat(label: str, value, icon: str = CHECK):
    print(f"  {icon} {label}: {BOLD}{value}{RESET}")


def run_pipeline(db_path: str | None = None, verbose: bool = True) -> PipelineResult:
    """
    Run the full B2B Lead Engine pipeline.

    Funnel (tracked at company level — progressive decrease):
        1. Pool        — All generated companies (TAM)
        2. Discovered  — Companies matching ICP criteria
        3. Enriched    — Companies successfully enriched (~85%)
        4. Scored      — All enriched leads scored
        5. Qualified   — Leads with score ≥ 80
        6. CRM Deals   — Qualified + Nurture synced
    """
    start_time = time.time()
    random.seed(42)

    if verbose:
        print(f"\n{ROCKET} {BOLD}B2B AUTONOMOUS LEAD ENGINE{RESET} {ROCKET}")
        print(f"{'─' * 60}")
        print(f"  Pipeline starting...")

    # ── Initialize ────────────────────────────────────
    db = Database(db_path or settings.database_path)
    icp_config = load_icp_config(settings.icp_config_path)

    # ════════════════════════════════════════════════════
    # STAGE 0: Generate TAM (Total Addressable Market)
    # ════════════════════════════════════════════════════
    all_companies = generate_seed_companies()
    all_contacts = generate_seed_contacts(all_companies)

    # Store ALL companies in the database (the full TAM pool)
    for company in all_companies:
        db.insert_company(company)
    for contact in all_contacts:
        db.insert_contact(contact)

    if verbose:
        _header(0, "MARKET POOL (TAM)")
        _stat("Total companies in pool", len(all_companies))
        _stat("Total contacts", len(all_contacts))

    # ════════════════════════════════════════════════════
    # STAGE 1: Lead Discovery (ICP Filter)
    # ════════════════════════════════════════════════════
    if verbose:
        _header(1, "AUTONOMOUS LEAD DISCOVERY")

    discovery = DiscoveryEngine(icp_config)
    # Pass the SAME objects to discovery so UUIDs are consistent across all tables
    discovered_companies, discovered_contacts = discovery.discover(
        companies=all_companies,
        contacts=all_contacts,
    )

    if verbose:
        stats = discovery.get_discovery_stats(discovered_companies, discovered_contacts)
        _stat("Companies matching ICP", stats["total_companies"])
        _stat("Contacts found", stats["total_contacts"])
        for country, count in stats["by_country"].items():
            flag = "🌎" if country == "US" else ("🇧🇷" if country == "BR" else "🌍")
            _stat(f"  {country}", count, f"  {flag}")
        pct = len(discovered_companies) / len(all_companies) * 100
        _stat("ICP match rate", f"{pct:.0f}%")

    # ════════════════════════════════════════════════════
    # STAGE 2: Lead Enrichment (with partial success)
    # ════════════════════════════════════════════════════
    if verbose:
        _header(2, "LEAD ENRICHMENT & PROFILING")

    # Simulate ~85% enrichment success rate
    enrichment_rate = 0.85
    enrichable_companies = [
        c for c in discovered_companies if random.random() < enrichment_rate
    ]
    enrichable_ids = {c.company_id for c in enrichable_companies}
    enrichable_contacts = [c for c in discovered_contacts if c.company_id in enrichable_ids]

    enrichment = EnrichmentPipeline()
    enriched_leads = enrichment.enrich(enrichable_companies, enrichable_contacts)

    for lead in enriched_leads:
        db.insert_enriched_lead(lead)

    if verbose:
        stats = enrichment.get_enrichment_stats(enriched_leads)
        _stat("Companies enriched", len(enrichable_companies))
        _stat("Leads enriched (contacts)", stats["total_enriched"])
        _stat("Avg completeness", f"{stats['avg_completeness']*100:.0f}%")
        _stat("Leads with tech gaps", stats["leads_with_tech_gaps"])
        _stat("Enrichment success rate", f"{len(enrichable_companies)}/{len(discovered_companies)}")

    # ════════════════════════════════════════════════════
    # STAGE 3: Lead Scoring & Qualification
    # ════════════════════════════════════════════════════
    if verbose:
        _header(3, "LEAD SCORING & QUALIFICATION")

    scoring = ScoringEngine(icp_config)
    scored_leads = scoring.score_leads(enriched_leads)

    # Generate deal briefs for qualified + nurture leads
    brief_gen = DealBriefGenerator()
    for lead in scored_leads:
        if lead.qualification_status.value in ["qualified", "nurture"]:
            brief = brief_gen.generate_brief(lead)
            lead.deal_brief = brief.to_text()

    for lead in scored_leads:
        db.insert_scored_lead(lead)

    qualified = [l for l in scored_leads if l.qualification_status.value == "qualified"]
    nurture = [l for l in scored_leads if l.qualification_status.value == "nurture"]
    disqualified = [l for l in scored_leads if l.qualification_status.value == "disqualified"]

    if verbose:
        stats = scoring.get_scoring_stats(scored_leads)
        _stat("Leads scored", stats["total_scored"], CHART)
        _stat("Average score", f"{stats['avg_score']}/100", CHART)
        _stat("Score range", f"{stats['min_score']} — {stats['max_score']}", CHART)
        print()
        _stat(f"Qualified (≥80)", len(qualified), f"  {GREEN}✅{RESET}")
        _stat(f"Nurture (60-79)", len(nurture), f"  {YELLOW}⚠️{RESET}")
        _stat(f"Disqualified (<60)", len(disqualified), f"  {RED}❌{RESET}")
        print(f"\n  {BOLD}BANT Qualification:{RESET}")
        for signal, count in stats.get("bant_met", {}).items():
            _stat(f"  {signal.title()}", f"{count}/{stats['total_scored']}", "  📋")

    # ════════════════════════════════════════════════════
    # STAGE 4: Automated SDR Outreach
    # ════════════════════════════════════════════════════
    if verbose:
        _header(4, "AUTOMATED SDR OUTREACH")

    # Only send outreach to qualified + nurture
    outreach_eligible = qualified + nurture
    outreach = OutreachEngine()
    outreach_events = outreach.generate_sequences(outreach_eligible)

    for event in outreach_events:
        db.insert_outreach_event(event)

    if verbose:
        stats = outreach.get_outreach_stats(outreach_events)
        _stat("Outreach events", stats["total_events"], MAIL)
        _stat("Emails sent", stats["sent"], MAIL)
        _stat("Open rate", f"{stats['open_rate']}%", MAIL)
        _stat("Reply rate", f"{stats['reply_rate']}%", MAIL)
        if stats.get("by_response_type"):
            print(f"\n  {BOLD}Response Types:{RESET}")
            for rtype, count in stats["by_response_type"].items():
                _stat(f"  {rtype.replace('_', ' ').title()}", count, "  💬")

    # ════════════════════════════════════════════════════
    # STAGE 5: CRM Sync & Handoff
    # ════════════════════════════════════════════════════
    if verbose:
        _header(5, "CRM SYNC & HANDOFF")

    crm = CRMSync()
    deals = crm.sync_leads(outreach_eligible, outreach_events)

    if verbose:
        crm_stats = crm.get_sync_stats()
        _stat("Deals synced to CRM", crm_stats["total_deals"], LINK)
        _stat("Total pipeline value", f"${crm_stats.get('total_pipeline_value', 0):,.2f}", LINK)
        if crm_stats.get("by_stage"):
            for stage, count in crm_stats["by_stage"].items():
                _stat(f"  {stage}", count, "  📁")

    # ════════════════════════════════════════════════════
    # RESULTS SUMMARY
    # ════════════════════════════════════════════════════
    elapsed = time.time() - start_time

    result = PipelineResult(
        companies_discovered=len(discovered_companies),
        contacts_found=len(discovered_contacts),
        leads_enriched=len(enriched_leads),
        leads_scored=len(scored_leads),
        leads_qualified=len(qualified),
        leads_nurture=len(nurture),
        leads_disqualified=len(disqualified),
        outreach_events_created=len(outreach_events),
        deals_synced_to_crm=len(deals),
        pipeline_duration_seconds=round(elapsed, 2),
    )

    if verbose:
        print(f"\n{'═' * 60}")
        print(f"{BOLD}{GREEN}  ✅ PIPELINE COMPLETE{RESET}")
        print(f"{'═' * 60}")
        print(f"\n  {BOLD}PROGRESSIVE FUNNEL:{RESET}")
        print(f"  {'─' * 50}")
        print(f"  🔷 Total Pool (TAM):     {len(all_companies):>5}")
        print(f"  🔷 ICP Discovered:       {len(discovered_companies):>5}  ({len(discovered_companies)/len(all_companies)*100:.0f}%)")
        print(f"  🔷 Enriched:             {len(enrichable_companies):>5}  ({len(enrichable_companies)/len(discovered_companies)*100:.0f}%)")
        print(f"  🔷 Scored:               {len(scored_leads):>5}  (contacts)")
        print(f"  {GREEN}🟢 Qualified:            {len(qualified):>5}{RESET}")
        print(f"  {YELLOW}🟡 Nurture:              {len(nurture):>5}{RESET}")
        print(f"  {RED}🔴 Disqualified:         {len(disqualified):>5}{RESET}")
        print(f"  🔷 CRM Deals:            {len(deals):>5}")
        print(f"  💰 Pipeline Value:        ${crm_stats.get('total_pipeline_value', 0):,.0f}")
        print(f"  ⏱️  Duration:             {elapsed:.2f}s")
        print(f"{'═' * 60}")

        # Show a sample deal brief
        qualified_with_briefs = [l for l in scored_leads if l.deal_brief]
        if qualified_with_briefs:
            print(f"\n{BOLD}{CYAN}📄 SAMPLE DEAL BRIEF:{RESET}\n")
            print(qualified_with_briefs[0].deal_brief)

    return result


# ── CLI Entry Point ───────────────────────────────────

if __name__ == "__main__":
    run_pipeline()
