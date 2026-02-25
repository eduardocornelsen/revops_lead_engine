"""
B2B Lead Engine — Simulated Business Metrics

Generates realistic time-series data, revenue metrics, SDR performance,
campaign attribution, forecast, and unit economics for dashboard visualization.
Deterministic (seeded) so charts are consistent across reloads.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np


def _seed():
    random.seed(2026)
    np.random.seed(2026)


# ── Time-Series: 90-Day Pipeline Activity ─────────────

def generate_daily_pipeline(days: int = 730) -> list[dict]:
    """Simulate exactly 730 days (2 years) of pipeline activity with realistic growth."""
    _seed()
    data = []
    base_date = datetime(2024, 2, 25)

    base_leads = 12
    base_revenue = 42_000

    for i in range(days):
        date = base_date + timedelta(days=i)
        dow = date.weekday()

        weekend_factor = 0.15 if dow >= 5 else 1.0
        growth = 1 + (i / days) * 0.5
        noise = max(0.5, np.random.normal(1.0, 0.18))

        leads_generated = max(1, int(base_leads * growth * weekend_factor * noise))
        leads_qualified = max(0, int(leads_generated * np.random.uniform(0.35, 0.55)))
        meetings_booked = max(0, int(leads_qualified * np.random.uniform(0.45, 0.70)))
        deals_won = max(0, int(meetings_booked * np.random.uniform(0.25, 0.50)))

        revenue = round(deals_won * base_revenue * np.random.uniform(0.8, 1.6), -2)
        emails_sent = max(0, int(leads_generated * 3 * weekend_factor * noise))
        emails_opened = int(emails_sent * np.random.uniform(0.35, 0.55))
        emails_replied = int(emails_opened * np.random.uniform(0.08, 0.18))

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "date_obj": date,
            "week": date.isocalendar()[1],
            "leads_generated": leads_generated,
            "leads_qualified": leads_qualified,
            "meetings_booked": meetings_booked,
            "deals_won": deals_won,
            "revenue": revenue,
            "pipeline_value": round(leads_qualified * base_revenue * 2.5 * growth, -2),
            "emails_sent": emails_sent,
            "emails_opened": emails_opened,
            "emails_replied": emails_replied,
        })

    return data


# ── Revenue Metrics with Period Comparisons ───────────

def generate_revenue_metrics(daily: list[dict]) -> dict:
    """Calculate aggregate revenue KPIs with MoM deltas."""
    total_revenue = sum(d["revenue"] for d in daily)
    total_leads = sum(d["leads_generated"] for d in daily)
    total_qualified = sum(d["leads_qualified"] for d in daily)
    total_meetings = sum(d["meetings_booked"] for d in daily)
    total_deals = sum(d["deals_won"] for d in daily)
    total_pipeline = sum(d["pipeline_value"] for d in daily)

    # Period comparisons (last 30 vs previous 30)
    last_30 = daily[-30:]
    prev_30 = daily[-60:-30]

    def _delta(last, prev):
        l = sum(d[last] if isinstance(last, str) else last for d in last_30) if isinstance(last, str) else last
        p = sum(d[prev] if isinstance(prev, str) else prev for d in prev_30) if isinstance(prev, str) else prev
        return ((l - p) / p * 100) if p else 0

    rev_last = sum(d["revenue"] for d in last_30)
    rev_prev = sum(d["revenue"] for d in prev_30)
    leads_last = sum(d["leads_generated"] for d in last_30)
    leads_prev = sum(d["leads_generated"] for d in prev_30)
    qual_last = sum(d["leads_qualified"] for d in last_30)
    qual_prev = sum(d["leads_qualified"] for d in prev_30)
    meetings_last = sum(d["meetings_booked"] for d in last_30)
    meetings_prev = sum(d["meetings_booked"] for d in prev_30)
    deals_last = sum(d["deals_won"] for d in last_30)
    deals_prev = sum(d["deals_won"] for d in prev_30)

    avg_deal_size = total_revenue / total_deals if total_deals else 0
    win_rate = total_deals / total_meetings * 100 if total_meetings else 0
    conversion_rate = total_qualified / total_leads * 100 if total_leads else 0

    # Sales velocity
    avg_cycle_days = 28
    velocity = (total_deals * avg_deal_size * (win_rate / 100)) / avg_cycle_days if avg_cycle_days else 0

    # Pipeline coverage ratio
    quarterly_target = 2_500_000
    active_pipeline = total_pipeline * 0.15  # realistic active vs total
    coverage_ratio = active_pipeline / quarterly_target if quarterly_target else 0

    # Unit economics
    total_spend = 37_800  # total campaign spend
    cac = total_spend / total_deals if total_deals else 0
    ltv = avg_deal_size * 2.8  # assume 2.8x expansion
    ltv_cac = ltv / cac if cac else 0

    return {
        "total_revenue": total_revenue,
        "total_pipeline": total_pipeline,
        "active_pipeline": active_pipeline,
        "total_leads": total_leads,
        "total_qualified": total_qualified,
        "total_meetings": total_meetings,
        "total_deals": total_deals,
        "avg_deal_size": avg_deal_size,
        "win_rate": win_rate,
        "conversion_rate": conversion_rate,
        "sales_velocity": velocity,
        "avg_cycle_days": avg_cycle_days,
        "coverage_ratio": coverage_ratio,
        # Deltas (MoM)
        "rev_growth_pct": ((rev_last - rev_prev) / rev_prev * 100) if rev_prev else 0,
        "leads_growth_pct": ((leads_last - leads_prev) / leads_prev * 100) if leads_prev else 0,
        "qual_growth_pct": ((qual_last - qual_prev) / qual_prev * 100) if qual_prev else 0,
        "meetings_growth_pct": ((meetings_last - meetings_prev) / meetings_prev * 100) if meetings_prev else 0,
        "deals_growth_pct": ((deals_last - deals_prev) / deals_prev * 100) if deals_prev else 0,
        # Period values
        "rev_last_30": rev_last, "rev_prev_30": rev_prev,
        "leads_last_30": leads_last, "leads_prev_30": leads_prev,
        "deals_last_30": deals_last, "deals_prev_30": deals_prev,
        # Targets
        "revenue_target": quarterly_target,
        "leads_target": 500,
        "meetings_target": 120,
        "quota_attainment": total_revenue / quarterly_target * 100,
        # Unit economics
        "cac": cac,
        "ltv": ltv,
        "ltv_cac_ratio": ltv_cac,
        "total_spend": total_spend,
    }


# ── Forecast by Stage Probability ─────────────────────

def generate_forecast(active_pipeline: float = 1_947_000) -> dict:
    """Weighted pipeline forecast by deal stage, scaled to match the true active pipeline."""
    _seed()
    
    # Base proportions
    stages = [
        {"stage": "Discovery", "probability": 0.10, "deals": 12, "weight": 0.30},
        {"stage": "Qualification", "probability": 0.25, "deals": 8, "weight": 0.22},
        {"stage": "Proposal Sent", "probability": 0.50, "deals": 6, "weight": 0.18},
        {"stage": "Negotiation", "probability": 0.75, "deals": 4, "weight": 0.11},
        {"stage": "Verbal Commit", "probability": 0.90, "deals": 3, "weight": 0.08},
        {"stage": "Closed Won", "probability": 1.00, "deals": 5, "weight": 0.11},
    ]
    
    # Scale values to exactly match the active_pipeline total
    for s in stages:
        s["value"] = round(active_pipeline * s["weight"], -2)
    total_unweighted = sum(s["value"] for s in stages)
    total_weighted = sum(s["value"] * s["probability"] for s in stages)
    best_case = sum(s["value"] for s in stages if s["probability"] >= 0.25)
    worst_case = sum(s["value"] * s["probability"] for s in stages if s["probability"] >= 0.50)

    return {
        "stages": stages,
        "total_unweighted": total_unweighted,
        "total_weighted": total_weighted,
        "best_case": best_case,
        "worst_case": worst_case,
    }


# ── Post-Sales & Expansion (Retention) ────────────────

def generate_post_sales_metrics() -> dict:
    """Generates simulated Net Dollar Retention (NDR) and Account Health KPIs."""
    _seed()
    
    # Base Recurring Revenue stats
    starting_arr = 12_500_000
    new_logo_arr = 1_850_000
    expansion_arr = 1_400_000  # Up-sells, cross-sells
    contraction_arr = 250_000  # Down-sells
    churn_arr = 400_000        # Dropped logos
    
    ending_arr = starting_arr + new_logo_arr + expansion_arr - contraction_arr - churn_arr
    
    # Retention formulas
    # Gross Retention = (Starting - Contraction - Churn) / Starting
    grr = (starting_arr - contraction_arr - churn_arr) / starting_arr * 100
    
    # Net Dollar Retention = (Starting + Expansion - Contraction - Churn) / Starting
    ndr = (starting_arr + expansion_arr - contraction_arr - churn_arr) / starting_arr * 100
    
    # Logo churn
    starting_logos = 420
    lost_logos = 12
    logo_churn_rate = (lost_logos / starting_logos) * 100
    
    # Account Health Score Tiers (out of 100)
    health = {
        "healthy": {"count": 315, "arr": ending_arr * 0.75, "color": "#10b981"},
        "at_risk": {"count": 65, "arr": ending_arr * 0.18, "color": "#f59e0b"},
        "critical": {"count": 28, "arr": ending_arr * 0.07, "color": "#ef4444"},
    }
    
    active_renewals_90d = 3_200_000

    return {
        "starting_arr": starting_arr,
        "ending_arr": ending_arr,
        "expansion_arr": expansion_arr,
        "ndr": ndr,
        "grr": grr,
        "logo_churn_rate": logo_churn_rate,
        "health_tiers": health,
        "active_renewals_90d": active_renewals_90d
    }


# ── Stage Velocity (avg days in each stage) ───────────

def generate_stage_velocity() -> list[dict]:
    """Average days deals spend in each pipeline stage."""
    _seed()
    return [
        {"stage": "Discovery", "avg_days": round(np.random.uniform(3, 8), 1),
         "target_days": 5, "deals_in_stage": 12},
        {"stage": "Qualification", "avg_days": round(np.random.uniform(5, 12), 1),
         "target_days": 7, "deals_in_stage": 8},
        {"stage": "Proposal Sent", "avg_days": round(np.random.uniform(4, 10), 1),
         "target_days": 5, "deals_in_stage": 6},
        {"stage": "Negotiation", "avg_days": round(np.random.uniform(6, 18), 1),
         "target_days": 10, "deals_in_stage": 4},
        {"stage": "Verbal Commit", "avg_days": round(np.random.uniform(2, 7), 1),
         "target_days": 3, "deals_in_stage": 3},
    ]


# ── Risk Alerts ───────────────────────────────────────

def generate_risk_alerts(sdr_data: list[dict]) -> list[dict]:
    """Generate actionable risk alerts for leadership."""
    _seed()
    low_reps = [s for s in sdr_data if s["attainment"] < 70]
    rep_alert_msg = (
        f"{low_reps[0]['name']} at {low_reps[0]['attainment']}% quota — needs coaching"
        if low_reps else "Lowest rep at 72% — monitor closely"
    )
    alerts = [
        {"severity": "high", "icon": "🔴", "type": "Stalled Pipeline",
         "message": "3 deals stuck in Negotiation >14 days — $215K at risk",
         "action": "Schedule exec sponsor calls for GrowthSolutions, MintTech, VeloAI"},
        {"severity": "high", "icon": "🔴", "type": "Rep Below Target",
         "message": rep_alert_msg,
         "action": "Review pipeline, pair with top performer for shadow calls"},
        {"severity": "medium", "icon": "🟡", "type": "Pipeline Coverage Low",
         "message": "Coverage ratio at 3.2x — below 4x target for Q1 close",
         "action": "Increase outbound volume by 20% or add new channel"},
        {"severity": "medium", "icon": "🟡", "type": "Conversion Drop",
         "message": "Proposal→Negotiation conversion dropped 12% WoW",
         "action": "Review last 5 lost proposals for objection patterns"},
        {"severity": "low", "icon": "🟢", "type": "Channel Opportunity",
         "message": "Referral channel has 4.2x ROI — highest in portfolio",
         "action": "Consider doubling referral program budget next quarter"},
    ]
    return alerts


# ── Campaign Attribution ──────────────────────────────

def generate_campaign_data() -> list[dict]:
    """Simulated campaign performance data."""
    _seed()
    campaigns = [
        {"name": "Apollo ICP Outbound", "source": "Apollo", "channel": "Email", "spend": 4_200},
        {"name": "LinkedIn Decision Makers", "source": "LinkedIn", "channel": "Social", "spend": 8_500},
        {"name": "Crunchbase Series A+", "source": "Crunchbase", "channel": "Email", "spend": 2_100},
        {"name": "Hunter.io Domain Blast", "source": "Hunter.io", "channel": "Email", "spend": 1_800},
        {"name": "Google Ads - RevOps", "source": "Google Ads", "channel": "Paid Search", "spend": 12_000},
        {"name": "Content Syndication", "source": "Organic", "channel": "Content", "spend": 3_200},
        {"name": "Referral Program", "source": "Referral", "channel": "Partner", "spend": 500},
        {"name": "Webinar: RevOps 2026", "source": "Event", "channel": "Webinar", "spend": 5_500},
    ]
    for c in campaigns:
        leads = int(np.random.uniform(15, 120))
        qualified = int(leads * np.random.uniform(0.25, 0.55))
        meetings = int(qualified * np.random.uniform(0.35, 0.65))
        deals = int(meetings * np.random.uniform(0.15, 0.40))
        revenue = round(deals * np.random.uniform(35_000, 85_000), -2)
        c.update({
            "leads": leads, "qualified": qualified, "meetings": meetings,
            "deals": deals, "revenue": revenue,
            "cpl": round(c["spend"] / leads, 2) if leads else 0,
            "roi": round((revenue - c["spend"]) / c["spend"] * 100, 1) if c["spend"] else 0,
        })
    return campaigns


# ── SDR Leaderboard with Activity Targets ─────────────

def generate_sdr_leaderboard() -> list[dict]:
    """Simulated SDR performance with daily/weekly targets."""
    _seed()
    sdrs = [
        "Sarah Chen", "Marcus Johnson", "Ana Oliveira", "David Kim",
        "Jessica Santos", "Rafael Costa", "Emily Davis", "Carlos Silva",
    ]
    data = []
    for name in sdrs:
        emails = int(np.random.uniform(180, 450))
        calls = int(np.random.uniform(60, 200))
        meetings = int(np.random.uniform(8, 35))
        pipeline = round(meetings * np.random.uniform(40_000, 90_000), -2)
        quota = 250_000

        # Daily targets
        emails_target_daily = 25
        calls_target_daily = 15
        meetings_target_weekly = 4
        days_worked = 20  # business days in month

        data.append({
            "name": name,
            "emails_sent": emails,
            "calls_made": calls,
            "meetings_booked": meetings,
            "pipeline_generated": pipeline,
            "quota": quota,
            "attainment": round(pipeline / quota * 100, 1),
            "response_rate": round(np.random.uniform(5, 18), 1),
            # Activity rates
            "emails_per_day": round(emails / days_worked, 1),
            "calls_per_day": round(calls / days_worked, 1),
            "meetings_per_week": round(meetings / 4, 1),
            # Targets
            "emails_target_daily": emails_target_daily,
            "calls_target_daily": calls_target_daily,
            "meetings_target_weekly": meetings_target_weekly,
            # Activity compliance
            "email_compliance": round(emails / (days_worked * emails_target_daily) * 100, 1),
            "call_compliance": round(calls / (days_worked * calls_target_daily) * 100, 1),
        })
    return sorted(data, key=lambda x: x["pipeline_generated"], reverse=True)


# ── Weekly Aggregation ────────────────────────────────

def aggregate_weekly(daily: list[dict]) -> list[dict]:
    """Roll up daily data into weekly summaries."""
    weeks = {}
    for d in daily:
        w = d["week"]
        if w not in weeks:
            weeks[w] = {
                "week": w, "start_date": d["date"],
                "leads_generated": 0, "leads_qualified": 0,
                "meetings_booked": 0, "deals_won": 0,
                "revenue": 0, "pipeline_value": 0,
                "emails_sent": 0, "emails_opened": 0, "emails_replied": 0,
            }
        for key in ["leads_generated", "leads_qualified", "meetings_booked",
                     "deals_won", "revenue", "pipeline_value",
                     "emails_sent", "emails_opened", "emails_replied"]:
            weeks[w][key] += d[key]
    return list(weeks.values())


# ── SFDC Opportunities ────────────────────────────────

def generate_sfdc_opportunities() -> list[dict]:
    """Simulate Salesforce-style opportunity records."""
    _seed()
    owners = ["Sarah Chen", "Marcus Johnson", "Ana Oliveira", "David Kim",
              "Jessica Santos", "Rafael Costa", "Emily Davis", "Carlos Silva"]

    companies = [
        ("MintTech", "Enterprise Software", "US"), ("GrowthSolutions", "MarTech", "US"),
        ("VeloAI", "AI/ML Platform", "US"), ("DataCore Inc", "Data Analytics", "US"),
        ("CloudSphere", "Cloud Infrastructure", "US"), ("SecureNet Pro", "Cybersecurity", "US"),
        ("Orbit Health", "HealthTech", "US"), ("NexaPay", "FinTech", "US"),
        ("RetailEdge", "RetailTech", "US"), ("StackValid", "DevOps Tools", "US"),
        ("TechBridge BR", "Software", "BR"), ("Dados Digital", "Tecnologia da Informação", "BR"),
        ("Agro Solutions", "AgriTech", "BR"), ("PropNow", "PropTech", "US"),
        ("LegalEase AI", "Legal Tech", "US"), ("EdVantage", "EdTech", "US"),
        ("HireSync", "HR Tech", "US"), ("RevFlow", "RevOps / Sales Tech", "US"),
    ]

    stages_prob = [
        ("Discovery", 0.10), ("Qualification", 0.25), ("Demo/POC", 0.40),
        ("Proposal Sent", 0.50), ("Negotiation", 0.75),
        ("Verbal Commit", 0.90), ("Closed Won", 1.00), ("Closed Lost", 0.00),
    ]

    opps = []
    base = datetime(2026, 2, 25)
    for _ in range(15):  # multiply list of companies to simulate more volume over 2 years
        for i, (company, industry, country) in enumerate(companies):
            stage_idx = int(np.random.choice(len(stages_prob), p=[0.12,0.14,0.12,0.15,0.14,0.08,0.15,0.10]))
            stage, prob = stages_prob[stage_idx]
            amount = round(np.random.uniform(25_000, 180_000), -3)
            # Spread across 730 days (2 years)
            created = base - timedelta(days=int(np.random.uniform(8, 730)))
            close_date = base + timedelta(days=int(np.random.uniform(-10, 60)))
            age = (base - created).days
            last_activity = base - timedelta(days=int(np.random.uniform(0, 14)))

        next_steps = {
            "Discovery": "Schedule discovery call",
            "Qualification": "Send qualification questionnaire",
            "Demo/POC": "Demo scheduled for next week",
            "Proposal Sent": "Follow up on proposal",
            "Negotiation": "Legal review in progress",
            "Verbal Commit": "Waiting for PO",
            "Closed Won": "Onboarding started",
            "Closed Lost": "Post-mortem scheduled",
        }

        opps.append({
            "opp_id": f"OPP-{1000+i}",
            "company": company,
            "industry": industry,
            "country": country,
            "stage": stage,
            "probability": prob,
            "amount": amount,
            "weighted_amount": round(amount * prob, -2),
            "owner": owners[i % len(owners)],
            "created_date": created.strftime("%Y-%m-%d"),
            "close_date": close_date.strftime("%Y-%m-%d"),
            "age_days": age,
            "last_activity": last_activity.strftime("%Y-%m-%d"),
            "days_since_activity": (base - last_activity).days,
            "next_step": next_steps[stage],
            "is_at_risk": age > 45 and prob < 0.75,
            "is_stalled": (base - last_activity).days > 10,
        })
    return opps


# ── Period Filter Helper ──────────────────────────────

def filter_daily_by_dates(daily: list[dict], start_date=None, end_date=None):
    """Filter daily data by actual dates, return (current, previous) of equal length."""
    from datetime import datetime
    if start_date and end_date:
        sd = start_date if isinstance(start_date, str) else start_date.strftime("%Y-%m-%d")
        ed = end_date if isinstance(end_date, str) else end_date.strftime("%Y-%m-%d")
        current = [d for d in daily if sd <= d["date"] <= ed]
        span = len(current)
        idx = daily.index(current[0]) if current else 0
        previous = daily[max(0, idx - span):idx]
    else:
        current = daily
        previous = []
    return current, previous


def get_daily_date_range(daily: list[dict]):
    """Return (min_date, max_date) from daily data."""
    from datetime import datetime
    dates = [datetime.strptime(d["date"], "%Y-%m-%d").date() for d in daily]
    return min(dates), max(dates)


# ── Per-Rep Daily Data ────────────────────────────────

SDR_NAMES = ["Sarah Chen", "Marcus Johnson", "Ana Oliveira", "David Kim",
             "Jessica Santos", "Rafael Costa", "Emily Davis", "Carlos Silva"]

def generate_daily_by_rep(daily: list[dict]) -> dict[str, list[dict]]:
    """Split daily data into per-rep allocations with realistic variance.
    Top performers close ~3-4x more than bottom performers."""
    _seed()
    # Fixed performance profiles — realistic B2B variance
    # Star performer → underperformer spread = 3.6x
    BASE_PROFILES = {
        "Sarah Chen":       1.80,  # Star — 22% of pipeline
        "Marcus Johnson":   1.55,  # Strong — 19%
        "Ana Oliveira":     1.10,  # Above avg — 14%
        "David Kim":        0.95,  # Average — 12%
        "Jessica Santos":   0.90,  # Average — 11%
        "Rafael Costa":     0.70,  # Below avg — 9%
        "Emily Davis":      0.55,  # Ramping — 7%
        "Carlos Silva":     0.45,  # New hire — 5%
    }
    total_w = sum(BASE_PROFILES.values())
    rep_data = {name: [] for name in SDR_NAMES}
    for d in daily:
        # Add daily jitter ±15% around the base profile
        weights = np.array([
            BASE_PROFILES[name] * np.random.uniform(0.85, 1.15)
            for name in SDR_NAMES
        ])
        weights /= weights.sum()

        # For sparse integers (deals, meetings), assign probabilistically
        deal_counts = [0] * len(SDR_NAMES)
        for _ in range(d["deals_won"]):
            winner = np.random.choice(len(SDR_NAMES), p=weights)
            deal_counts[winner] += 1

        mtg_counts = [0] * len(SDR_NAMES)
        for _ in range(d["meetings_booked"]):
            winner = np.random.choice(len(SDR_NAMES), p=weights)
            mtg_counts[winner] += 1

        for i, name in enumerate(SDR_NAMES):
            w = weights[i]
            # Revenue follows deals — if rep got deals, they get proportional revenue
            rep_rev = round(d["revenue"] * deal_counts[i] / max(1, d["deals_won"]), -2) if d["deals_won"] > 0 else round(d["revenue"] * w, -2)
            rep_data[name].append({
                "date": d["date"], "date_obj": d["date_obj"], "week": d["week"],
                "leads_generated": max(0, int(d["leads_generated"] * w)),
                "leads_qualified": max(0, int(d["leads_qualified"] * w)),
                "meetings_booked": mtg_counts[i],
                "deals_won": deal_counts[i],
                "revenue": rep_rev,
                "pipeline_value": round(d["pipeline_value"] * w, -2),
                "emails_sent": max(0, int(d["emails_sent"] * w)),
                "emails_opened": max(0, int(d["emails_opened"] * w)),
                "emails_replied": max(0, int(d["emails_replied"] * w)),
            })
    return rep_data


def compute_period_metrics(current: list[dict], previous: list[dict],
                            is_individual_rep: bool = False) -> dict:
    """Compute metrics for filtered period with comparison deltas.
    If is_individual_rep, quota target = team_target / 8."""
    def _sum(data, key):
        return sum(d[key] for d in data)

    def _delta(curr_val, prev_val):
        if not prev_val: return 0
        return ((curr_val - prev_val) / prev_val * 100)

    total_revenue = _sum(current, "revenue")
    total_leads = _sum(current, "leads_generated")
    total_qualified = _sum(current, "leads_qualified")
    total_meetings = _sum(current, "meetings_booked")
    total_deals = _sum(current, "deals_won")
    total_pipeline = _sum(current, "pipeline_value")
    total_emails = _sum(current, "emails_sent")
    total_opened = _sum(current, "emails_opened")
    total_replied = _sum(current, "emails_replied")

    prev_rev = _sum(previous, "revenue") if previous else 0
    prev_leads = _sum(previous, "leads_generated") if previous else 0
    prev_qual = _sum(previous, "leads_qualified") if previous else 0
    prev_meetings = _sum(previous, "meetings_booked") if previous else 0
    prev_deals = _sum(previous, "deals_won") if previous else 0

    avg_deal = total_revenue / total_deals if total_deals else 0
    win_rate = total_deals / total_meetings * 100 if total_meetings else 0
    conversion = total_qualified / total_leads * 100 if total_leads else 0

    # Scale targets for individual rep
    team_target = 2_500_000
    team_spend = 37_800
    n_reps = 8
    quarterly_target = team_target / n_reps if is_individual_rep else team_target
    total_spend = team_spend / n_reps if is_individual_rep else team_spend

    # Unit economics
    cac = total_spend / total_deals if total_deals else 0
    ltv = avg_deal * 2.8
    ltv_cac = ltv / cac if cac else 0

    active_pipeline = total_pipeline * 0.15
    coverage = active_pipeline / quarterly_target if quarterly_target else 0

    avg_cycle = 28
    velocity = (total_deals * avg_deal * (win_rate / 100)) / avg_cycle if avg_cycle else 0

    prev_pipeline = _sum(previous, "pipeline_value") if previous else 0
    prev_active_pipeline = prev_pipeline * 0.15 if previous else 0
    pipe_delta = _delta(active_pipeline, prev_active_pipeline)

    prev_avg_deal = prev_rev / prev_deals if prev_deals else 0
    avg_deal_delta = _delta(avg_deal, prev_avg_deal)

    prev_win_rate = prev_deals / prev_meetings * 100 if prev_meetings else 0
    win_rate_delta = win_rate - prev_win_rate

    prev_avg_cycle = 28
    prev_velocity = (prev_deals * prev_avg_deal * (prev_win_rate / 100)) / prev_avg_cycle if prev_avg_cycle else 0
    velocity_delta = _delta(velocity, prev_velocity)

    date_from = current[0]["date"] if current else "—"
    date_to = current[-1]["date"] if current else "—"

    quota_attainment = total_revenue / quarterly_target * 100 if quarterly_target else 0

    return {
        "total_revenue": total_revenue, "total_pipeline": total_pipeline,
        "active_pipeline": active_pipeline,
        "total_leads": total_leads, "total_qualified": total_qualified,
        "total_meetings": total_meetings, "total_deals": total_deals,
        "total_emails": total_emails, "total_opened": total_opened,
        "total_replied": total_replied,
        "avg_deal_size": avg_deal, "win_rate": win_rate,
        "conversion_rate": conversion, "sales_velocity": velocity,
        "avg_cycle_days": avg_cycle, "coverage_ratio": coverage,
        # Deltas
        "rev_delta": _delta(total_revenue, prev_rev),
        "leads_delta": _delta(total_leads, prev_leads),
        "qual_delta": _delta(total_qualified, prev_qual),
        "meetings_delta": _delta(total_meetings, prev_meetings),
        "deals_delta": _delta(total_deals, prev_deals),
        "pipe_delta": pipe_delta,
        "avg_deal_delta": avg_deal_delta,
        "win_delta": win_rate_delta,
        "vel_delta": velocity_delta,
        "cycle_delta": 0,
        "has_comparison": len(previous) > 0,
        # Unit economics
        "cac": cac, "ltv": ltv, "ltv_cac_ratio": ltv_cac,
        "total_spend": total_spend,
        # Targets
        "revenue_target": quarterly_target,
        "quota_attainment": quota_attainment,
        "quota_revenue": total_revenue,
        "quota_target_amount": quarterly_target,
        "is_individual_rep": is_individual_rep,
        # Date range
        "date_from": date_from, "date_to": date_to,
        "period_days": len(current),
    }

