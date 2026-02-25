"""
B2B Lead Engine — Stage 3: Lead Scoring Engine

Rule-based lead scoring (0–100) with BANT pre-qualification.
Designed for easy swap to Scikit-learn/XGBoost model.
"""

from __future__ import annotations

from src.config.icp_loader import ICPConfig, get_active_profiles
from src.models.models import (
    EnrichedLead,
    ScoredLead,
    ScoreBreakdown,
    QualificationStatus,
)


# ── Scoring Weights (from ICP config) ─────────────────

DEFAULT_WEIGHTS = {
    "firmographic_fit": 0.30,
    "behavioral_signals": 0.25,
    "tech_stack_gap": 0.25,
    "engagement_signals": 0.20,
}


class ScoringEngine:
    """
    Rule-based lead scoring engine.

    Scores leads 0–100 based on:
    - ICP firmographic fit (30%)
    - Behavioral/buying signals (25%)
    - Tech stack gaps = selling opportunities (25%)
    - Engagement signals (20%)

    Also runs BANT pre-qualification checks.
    """

    def __init__(
        self,
        icp_config: ICPConfig,
        qualified_min: float = 80.0,
        nurture_min: float = 60.0,
    ):
        self.icp_config = icp_config
        self.profiles = get_active_profiles(icp_config)
        self.qualified_min = qualified_min
        self.nurture_min = nurture_min

        # Load weights from config or use defaults
        weights = icp_config.global_config.scoring_weights
        self.weights = {
            "firmographic_fit": weights.firmographic_fit,
            "behavioral_signals": weights.behavioral_signals,
            "tech_stack_gap": weights.tech_stack_gap,
            "engagement_signals": weights.engagement_signals,
        }

    def score_leads(self, enriched_leads: list[EnrichedLead]) -> list[ScoredLead]:
        """Score and qualify all enriched leads."""
        return [self.score_lead(lead) for lead in enriched_leads]

    def score_lead(self, lead: EnrichedLead) -> ScoredLead:
        """Score and qualify a single enriched lead."""
        breakdown = self._compute_breakdown(lead)
        total_score = self._compute_total(breakdown)
        bant = self._check_bant(lead)
        status = self._qualify(total_score)
        deal_stage = self._map_deal_stage(status)

        return ScoredLead(
            lead_id=lead.lead_id,
            score=round(total_score, 1),
            score_breakdown=breakdown,
            qualification_status=status,
            budget_signal=bant["budget"],
            authority_signal=bant["authority"],
            need_signal=bant["need"],
            timeline_signal=bant["timeline"],
            deal_stage=deal_stage,
            enriched_lead=lead,
        )

    def _compute_breakdown(self, lead: EnrichedLead) -> ScoreBreakdown:
        """Compute individual score components (each 0–100 scale) with explainability."""
        reasons = []

        # ── ICP Fit Score ─────────────────────────────
        icp_score = 0.0
        if lead.company:
            c = lead.company
            # Revenue fit (higher = better, up to a point)
            if 2_000_000 <= c.revenue_usd <= 100_000_000:
                icp_score += 25
                reasons.append(f"Strong revenue fit ({c.revenue_usd/1e6:.1f}M) (+25 ICP)")
            elif c.revenue_usd > 0:
                icp_score += 10
                reasons.append(f"Basic revenue fit (+10 ICP)")

            # Employee count fit
            if 50 <= c.employee_count <= 1000:
                icp_score += 25
                reasons.append(f"Sweet-spot employee count ({c.employee_count}) (+25 ICP)")
            elif c.employee_count > 0:
                icp_score += 10
                reasons.append(f"Basic employee count fit (+10 ICP)")

            # Industry match
            for profile in self.profiles:
                if c.industry in profile.firmographic_filters.industries:
                    icp_score += 25
                    reasons.append(f"Tier 1 Industry Match: {c.industry} (+25 ICP)")
                    break

            # Funding stage
            if c.funding_stage in ["Series A", "Series B", "Series C"]:
                icp_score += 25
                reasons.append(f"High-growth funding stage: {c.funding_stage} (+25 ICP)")
            elif c.funding_stage:
                icp_score += 10
                reasons.append(f"Funded company: {c.funding_stage} (+10 ICP)")

        # ── Behavioral Score ──────────────────────────
        behavioral_score = 0.0
        signals = lead.buying_signals
        if signals:
            # High-intent signals worth more
            high_intent_keywords = ["funding", "hiring", "SDR", "CRO", "VP", "RevOps"]
            high_count = sum(
                1 for s in signals
                if any(kw.lower() in s.lower() for kw in high_intent_keywords)
            )
            base_b = len(signals) * 15
            bonus_b = high_count * 10
            behavioral_score = min(100, base_b + bonus_b)
            if high_count > 0:
                reasons.append(f"Detected {high_count} high-intent executive buying signals (+{bonus_b} Behavior)")
            if len(signals) > 0:
                reasons.append(f"Active in-market signals detected (+{min(100, base_b)} Behavior)")

        # ── Tech Gap Score ────────────────────────────
        tech_score = 0.0
        if lead.tech_stack_gaps:
            pts = min(100, len(lead.tech_stack_gaps) * 35)
            tech_score = pts
            reasons.append(f"Identified {len(lead.tech_stack_gaps)} critical tech stack gaps (+{pts} Needs)")

        if lead.tech_stack_detected:
            enterprise_tools = ["Salesforce", "SAP", "Oracle"]
            detected_ent = [t for t in enterprise_tools if t in lead.tech_stack_detected]
            if detected_ent:
                penalty = 30
                tech_score = max(0, tech_score - penalty)
                reasons.append(f"Enterprise lock-in risk: uses {detected_ent[0]} (-{penalty} Needs penalty)")

        # ── Engagement Score ──────────────────────────
        engagement_score = 0.0
        social = lead.social_signals
        if social:
            posts = social.get("linkedin_posts_30d", 0)
            engagement_level = social.get("linkedin_engagement", "low")

            if posts > 5:
                engagement_score += 40
                reasons.append("Highly active content creator on LinkedIn (+40 Engagement)")
            elif posts > 0:
                engagement_score += 20
                reasons.append("Recent LinkedIn posting activity (+20 Engagement)")

            if engagement_level == "high":
                engagement_score += 30
                reasons.append("High reply/comment rate (+30 Engagement)")
            elif engagement_level == "medium":
                engagement_score += 15

            if social.get("twitter_active"):
                engagement_score += 15

        # Enrichment completeness bonus
        bonus_e = int(lead.enrichment_completeness * 15)
        engagement_score = min(100, engagement_score + bonus_e)
        if bonus_e >= 10:
            reasons.append(f"High data enrichment confidence (+{bonus_e} Engagement bonus)")

        return ScoreBreakdown(
            icp_fit=round(icp_score, 1),
            behavioral=round(behavioral_score, 1),
            tech_gap=round(tech_score, 1),
            engagement=round(engagement_score, 1),
            reasons=reasons[:5]  # Keep top 5 most critical reasons
        )

    def _compute_total(self, breakdown: ScoreBreakdown) -> float:
        """Compute weighted total score."""
        total = (
            breakdown.icp_fit * self.weights["firmographic_fit"]
            + breakdown.behavioral * self.weights["behavioral_signals"]
            + breakdown.tech_gap * self.weights["tech_stack_gap"]
            + breakdown.engagement * self.weights["engagement_signals"]
        )
        return min(100.0, total)

    def _check_bant(self, lead: EnrichedLead) -> dict[str, bool]:
        """Run BANT (Budget, Authority, Need, Timeline) qualification."""
        budget = False
        authority = False
        need = False
        timeline = False

        if lead.company:
            # Budget: company has funding or significant revenue
            budget = (
                lead.company.revenue_usd >= 5_000_000
                or "funding" in " ".join(lead.buying_signals).lower()
            )

        if lead.contact:
            # Authority: contact is VP+, Director+, or C-level
            senior = ["VP", "C-Level", "Director", "Head", "CRO", "CMO", "CTO"]
            authority = any(
                s.lower() in lead.contact.seniority.lower()
                or s.lower() in lead.contact.title.lower()
                for s in senior
            )

        # Need: tech stack gaps detected
        need = len(lead.tech_stack_gaps) > 0

        # Timeline: active buying signals present
        timeline_keywords = ["hiring", "SDR", "new", "launched", "expansion"]
        timeline = any(
            any(kw.lower() in s.lower() for kw in timeline_keywords)
            for s in lead.buying_signals
        )

        return {
            "budget": budget,
            "authority": authority,
            "need": need,
            "timeline": timeline,
        }

    def _qualify(self, score: float) -> QualificationStatus:
        """Map score to qualification status."""
        if score >= self.qualified_min:
            return QualificationStatus.QUALIFIED
        elif score >= self.nurture_min:
            return QualificationStatus.NURTURE
        else:
            return QualificationStatus.DISQUALIFIED

    def _map_deal_stage(self, status: QualificationStatus) -> str:
        """Map qualification status to CRM deal stage."""
        stage_map = {
            QualificationStatus.QUALIFIED: "Qualified",
            QualificationStatus.NURTURE: "Nurture",
            QualificationStatus.DISQUALIFIED: "Disqualified",
        }
        return stage_map.get(status, "Unknown")

    def get_scoring_stats(self, scored_leads: list[ScoredLead]) -> dict:
        """Generate scoring statistics."""
        if not scored_leads:
            return {"total": 0}

        scores = [l.score for l in scored_leads]
        by_status = {}
        for lead in scored_leads:
            s = lead.qualification_status.value
            by_status[s] = by_status.get(s, 0) + 1

        bant_met = {
            "budget": sum(1 for l in scored_leads if l.budget_signal),
            "authority": sum(1 for l in scored_leads if l.authority_signal),
            "need": sum(1 for l in scored_leads if l.need_signal),
            "timeline": sum(1 for l in scored_leads if l.timeline_signal),
        }

        return {
            "total_scored": len(scored_leads),
            "avg_score": round(sum(scores) / len(scores), 1),
            "max_score": round(max(scores), 1),
            "min_score": round(min(scores), 1),
            "by_status": by_status,
            "bant_met": bant_met,
        }
