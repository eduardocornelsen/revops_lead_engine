"""
B2B Lead Engine — AI Deal Brief Generator

Generates SPIN questions, BANT summaries, call scripts,
and objection handling for qualified leads.

MVP uses prompt templates. Production uses LLM APIs.
"""

from __future__ import annotations

from src.models.models import DealBrief, ScoredLead, EnrichedLead


class DealBriefGenerator:
    """
    Generates AI-style deal briefs using prompt templates.

    Each brief includes:
    - Company context summary
    - BANT qualification summary
    - SPIN discovery questions (Situation, Problem, Implication, Need-Payoff)
    - Objection handling playbook
    - Discovery call script outline
    """

    # ── SPIN Question Templates ───────────────────────

    SPIN_TEMPLATES = {
        "CRM": [
            {"type": "S", "question": "How are you currently tracking your sales pipeline and deal stages?"},
            {"type": "P", "question": "What happens when a deal stalls — how does your team surface that?"},
            {"type": "I", "question": "If pipeline visibility takes 2 days to update, what does that cost in lost deals per quarter?"},
            {"type": "N", "question": "If you could see real-time stage conversion and auto-flag stalled deals, how would that change your forecast meetings?"},
        ],
        "Pipeline Management": [
            {"type": "S", "question": "How are you currently managing lead-to-close handoffs across your team?"},
            {"type": "P", "question": "Where do leads most often fall through the cracks in your current process?"},
            {"type": "I", "question": "What's the revenue impact of slow follow-up — how many deals does your team lose to delayed response?"},
            {"type": "N", "question": "What if you could automatically route and prioritize leads so your team only focuses on the highest-intent prospects?"},
        ],
        "Automated Reporting": [
            {"type": "S", "question": "How does your team currently compile sales reports and pipeline reviews?"},
            {"type": "P", "question": "How much time does your RevOps team spend building weekly reports manually?"},
            {"type": "I", "question": "When reports are delayed or inaccurate, how does that affect your leadership's ability to make decisions?"},
            {"type": "N", "question": "What if pipeline reports updated in real-time and automatically flagged risks and opportunities?"},
        ],
        "Dashboard": [
            {"type": "S", "question": "What tools does your leadership team use to review pipeline health?"},
            {"type": "P", "question": "How confident are you in the accuracy of your current pipeline data?"},
            {"type": "I", "question": "When forecasts miss, what's the impact on your team's credibility with the board?"},
            {"type": "N", "question": "What if your exec team could see live pipeline metrics, conversion rates, and risk alerts in one dashboard?"},
        ],
        "Real-time Analytics": [
            {"type": "S", "question": "How quickly can your team access up-to-date sales performance data?"},
            {"type": "P", "question": "What challenges do you face with data freshness in your current analytics setup?"},
            {"type": "I", "question": "How many decisions get delayed because the data isn't ready yet?"},
            {"type": "N", "question": "What if every metric updated in real-time, and anomalies were flagged automatically?"},
        ],
    }

    # ── Objection Templates ───────────────────────────

    OBJECTION_TEMPLATES = [
        {
            "objection": "We already use spreadsheets and it works fine",
            "response": "Spreadsheets work until you hit 50+ deals/month — then manual updates become your biggest bottleneck and data quality drops.",
        },
        {
            "objection": "We're evaluating other tools right now",
            "response": "Great — I can share how our approach reduces eval time by giving you a working proof-of-concept with your actual data.",
        },
        {
            "objection": "We don't have budget for new tools right now",
            "response": "Understood. What if I could show you the exact revenue being lost to manual processes — so you can build the business case?",
        },
        {
            "objection": "Our team is too busy to implement something new",
            "response": "That's exactly why automation matters — we handle the setup, and your team saves 15+ hours/week from day one.",
        },
        {
            "objection": "We tried a CRM before and it didn't work",
            "response": "Most CRM failures come from over-engineering. Our approach starts simple — track 3 metrics — and grows with your team.",
        },
    ]

    def generate_brief(self, scored_lead: ScoredLead) -> DealBrief:
        """Generate a deal brief for a scored lead."""
        enriched = scored_lead.enriched_lead
        if not enriched or not enriched.company or not enriched.contact:
            return DealBrief(
                lead_id=scored_lead.lead_id,
                company_name="Unknown",
            )

        company = enriched.company
        contact = enriched.contact

        # Build company summary
        revenue_str = f"${company.revenue_usd/1_000_000:.0f}M" if company.revenue_usd else "N/A"
        company_summary = (
            f"{company.name} | {company.industry} | "
            f"{company.employee_count} employees | {revenue_str} revenue"
        )

        # Build BANT summary
        bant = self._build_bant_summary(scored_lead, enriched)

        # Select SPIN questions based on tech gaps
        spin = self._select_spin_questions(enriched)

        # Select relevant objections
        objections = self._select_objections(enriched)

        # Build call script
        call_script = self._generate_call_script(company, contact, bant)

        brief = DealBrief(
            lead_id=scored_lead.lead_id,
            company_name=company.name,
            company_summary=company_summary,
            contact_name=contact.full_name,
            contact_title=contact.title,
            bant_summary=bant,
            spin_questions=spin,
            objection_handling=objections,
            call_script=call_script,
        )

        return brief

    def _build_bant_summary(
        self, scored: ScoredLead, enriched: EnrichedLead
    ) -> dict:
        """Build BANT qualification summary with details."""
        company = enriched.company
        contact = enriched.contact

        bant = {}

        # Budget
        if scored.budget_signal and company:
            detail = f"Revenue: ${company.revenue_usd/1_000_000:.0f}M"
            if company.funding_stage:
                detail += f" | {company.funding_stage}"
            bant["Budget"] = {"met": True, "detail": detail}
        else:
            bant["Budget"] = {"met": False, "detail": "No funding/revenue signal detected"}

        # Authority
        if scored.authority_signal and contact:
            bant["Authority"] = {
                "met": True,
                "detail": f"{contact.seniority}-level: {contact.title}",
            }
        else:
            bant["Authority"] = {"met": False, "detail": "Contact not VP+ level"}

        # Need
        if scored.need_signal:
            gaps = ", ".join(enriched.tech_stack_gaps[:3])
            bant["Need"] = {"met": True, "detail": f"Tech gaps: {gaps}"}
        else:
            bant["Need"] = {"met": False, "detail": "No significant tech gaps detected"}

        # Timeline
        if scored.timeline_signal:
            signals = [s for s in enriched.buying_signals[:2]]
            bant["Timeline"] = {
                "met": True,
                "detail": "; ".join(signals),
            }
        else:
            bant["Timeline"] = {
                "met": False,
                "detail": "No immediate buying signals",
            }

        return bant

    def _select_spin_questions(self, enriched: EnrichedLead) -> list[dict]:
        """Select SPIN questions based on detected tech gaps."""
        questions = []

        for gap in enriched.tech_stack_gaps:
            if gap in self.SPIN_TEMPLATES:
                questions.extend(self.SPIN_TEMPLATES[gap])
                break

        # Fallback to CRM questions if no gap-specific ones found
        if not questions:
            questions = self.SPIN_TEMPLATES.get("CRM", [])

        return questions[:4]  # Limit to 4 SPIN questions

    def _select_objections(self, enriched: EnrichedLead) -> list[dict]:
        """Select relevant objection handling based on tech stack."""
        objections = []

        # Check for spreadsheet usage
        spreadsheet_tools = ["Google Sheets", "Excel", "Sheets", "Planilhas"]
        if any(t in enriched.tech_stack_detected for t in spreadsheet_tools):
            objections.append(self.OBJECTION_TEMPLATES[0])

        # Always include general objections
        objections.extend(self.OBJECTION_TEMPLATES[1:4])

        return objections[:4]

    def _generate_call_script(
        self, company, contact, bant: dict
    ) -> str:
        """Generate a discovery call script."""
        met_count = sum(1 for v in bant.values() if v.get("met", False))

        script = f"""
DISCOVERY CALL SCRIPT — {company.name}

OPENER:
"Hi {contact.full_name.split()[0]}, this is [Your Name]. I noticed {company.name} is
 growing rapidly in {company.industry} — congratulations on the momentum.

I work with {company.industry} companies similar to yours that are scaling their
sales operations, and I had a quick question about how you're managing that growth."

TRANSITION TO DISCOVERY:
"I'm curious — as you've scaled from [estimate] to {company.employee_count} people,
how has your sales process evolved? Are you still using the same tools?"

KEY TALKING POINTS:
- BANT signals met: {met_count}/4
- Primary gap: {', '.join(list(bant.keys())[:2])}
- Approach: Focus on [{', '.join(k for k, v in bant.items() if v.get('met'))}]

CLOSE:
"Based on what you've shared, I think it would be valuable to show you how
companies like yours have [solved specific gap]. Would [day] at [time] work
for a 20-minute deep dive?"
""".strip()

        return script
