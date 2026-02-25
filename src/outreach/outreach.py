"""
B2B Lead Engine — Stage 4: Outreach Automation

Generates personalized multi-touch email sequences, classifies
responses, and tracks all outreach events.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta
from typing import Optional

from src.models.models import (
    ScoredLead,
    OutreachEvent,
    OutreachChannel,
    OutreachStatus,
    ResponseType,
)


class OutreachEngine:
    """
    Automated SDR outreach engine.

    Generates personalized 3-touch email sequences based on
    lead scoring and enrichment data.
    """

    # ── Email Templates ───────────────────────────────

    SUBJECT_TEMPLATES = {
        1: [
            "Quick question about {company}'s sales process",
            "{first_name}, noticed {company} is scaling — quick thought",
            "Re: {industry} pipeline challenge",
        ],
        2: [
            "Following up: {company}'s growth opportunity",
            "{first_name}, a {industry} case study you'd find relevant",
            "How {similar_company} solved the exact problem {company} faces",
        ],
        3: [
            "Last note — {company} pipeline efficiency",
            "{first_name}, worth 15 minutes?",
            "closing the loop: {company}",
        ],
    }

    BODY_TEMPLATES = {
        1: """Hi {first_name},

I noticed {company} has been growing rapidly in {industry} — congrats on the momentum.

I work with {industry} companies similar to yours that are scaling their revenue operations, and I noticed something interesting:

{personalization_hook}

I've helped companies like yours reduce SDR time-to-lead by 60% and increase qualified pipeline by 40% — all without adding headcount.

Would you be open to a 15-minute call this week to see if there's a fit?

Best,
[Your Name]""",

        2: """Hi {first_name},

Following up on my note last week. I wanted to share a quick case study:

One of our {industry} clients was struggling with {pain_point}. In 6 weeks, they:
• Cut lead response time from 3 days to 15 minutes
• Increased qualified meetings by 45%
• Automated 80% of their SDR prospecting workflow

{company} seems like it could benefit from a similar approach, especially given {buying_signal}.

Worth a quick chat? Here's my calendar: [booking link]

Best,
[Your Name]""",

        3: """Hi {first_name},

I know timing is everything, so I'll keep this brief.

If {company} is looking to optimize its sales pipeline this quarter, I'd love to show you how we help {industry} companies convert more leads with less manual work.

If now isn't the right time, no worries — I'll check back in Q{next_quarter}. But if you're curious, reply "interested" and I'll send over a quick overview.

Best,
[Your Name]""",
    }

    def generate_sequences(
        self, scored_leads: list[ScoredLead], steps: int = 3
    ) -> list[OutreachEvent]:
        """
        Generate multi-touch outreach sequences for scored leads.

        Only generates sequences for qualified and nurture leads.
        """
        events = []

        for lead in scored_leads:
            if lead.qualification_status.value == "disqualified":
                continue

            enriched = lead.enriched_lead
            if not enriched or not enriched.company or not enriched.contact:
                continue

            company = enriched.company
            contact = enriched.contact

            for step in range(1, steps + 1):
                subject = self._generate_subject(step, company, contact)
                body = self._generate_body(step, lead)

                # Simulate sending time (staggered)
                send_time = datetime.now(timezone.utc) + timedelta(days=(step - 1) * 3)

                event = OutreachEvent(
                    lead_id=lead.lead_id,
                    channel=OutreachChannel.EMAIL,
                    sequence_step=step,
                    subject=subject,
                    body=body,
                    status=OutreachStatus.SENT,
                    sent_at=send_time,
                )

                # Simulate responses for demo purposes
                event = self._simulate_response(event, step)
                events.append(event)

        return events

    def _generate_subject(self, step: int, company, contact) -> str:
        """Generate email subject line for a given sequence step."""
        templates = self.SUBJECT_TEMPLATES.get(step, self.SUBJECT_TEMPLATES[1])
        template = random.choice(templates)

        return template.format(
            company=company.name,
            first_name=contact.full_name.split()[0],
            industry=company.industry,
            similar_company="[Similar Co]",
        )

    def _generate_body(self, step: int, lead: ScoredLead) -> str:
        """Generate email body for a given sequence step."""
        template = self.BODY_TEMPLATES.get(step, self.BODY_TEMPLATES[1])
        enriched = lead.enriched_lead
        company = enriched.company
        contact = enriched.contact

        # Personalization hook based on enrichment
        hook = ""
        if enriched.tech_stack_gaps:
            hook = f"Your team appears to be using {', '.join(enriched.tech_stack_detected[:2])} — which works, but many teams at your stage are finding that automated pipeline tools help them scale faster."
        elif enriched.buying_signals:
            hook = f"Given {enriched.buying_signals[0].lower()}, you might be exploring ways to scale your sales operations more efficiently."

        # Pain point
        pain = "manual pipeline tracking and lead qualification"
        if enriched.tech_stack_gaps:
            pain = f"gaps in {', '.join(enriched.tech_stack_gaps[:2]).lower()}"

        # Buying signal
        signal = enriched.buying_signals[0] if enriched.buying_signals else "your recent growth"

        import datetime as dt
        quarter = (dt.datetime.now().month - 1) // 3 + 2
        if quarter > 4:
            quarter = 1

        return template.format(
            first_name=contact.full_name.split()[0],
            company=company.name,
            industry=company.industry,
            personalization_hook=hook,
            pain_point=pain,
            buying_signal=signal.lower(),
            next_quarter=quarter,
        )

    def _simulate_response(
        self, event: OutreachEvent, step: int
    ) -> OutreachEvent:
        """Simulate email responses for demo purposes."""
        # Simulate open rates (~60% step 1, lower after)
        open_rate = {1: 0.6, 2: 0.4, 3: 0.3}.get(step, 0.3)
        if random.random() < open_rate:
            event.status = OutreachStatus.OPENED
            event.opened_at = event.sent_at + timedelta(hours=random.randint(1, 48))

            # Simulate reply rates (~15% step 1, ~10% step 2, ~5% step 3)
            reply_rate = {1: 0.15, 2: 0.10, 3: 0.05}.get(step, 0.05)
            if random.random() < reply_rate:
                event.status = OutreachStatus.REPLIED
                event.responded_at = event.opened_at + timedelta(
                    hours=random.randint(1, 24)
                )
                event.response_type = random.choice([
                    ResponseType.INTERESTED,
                    ResponseType.NOT_NOW,
                    ResponseType.NOT_INTERESTED,
                ])

        return event

    def classify_response(self, response_text: str) -> ResponseType:
        """
        Classify an email response.
        MVP uses keyword matching; production uses LLM classification.
        """
        text = response_text.lower()

        positive = ["interested", "yes", "sure", "love to", "sounds good", "let's chat"]
        negative = ["not interested", "unsubscribe", "remove", "no thanks", "stop"]
        later = ["not now", "maybe later", "next quarter", "not the right time", "busy"]
        ooo = ["out of office", "vacation", "away", "returning"]

        if any(kw in text for kw in ooo):
            return ResponseType.OUT_OF_OFFICE
        elif any(kw in text for kw in positive):
            return ResponseType.INTERESTED
        elif any(kw in text for kw in negative):
            return ResponseType.NOT_INTERESTED
        elif any(kw in text for kw in later):
            return ResponseType.NOT_NOW
        else:
            return ResponseType.AUTO_REPLY

    def get_outreach_stats(self, events: list[OutreachEvent]) -> dict:
        """Generate outreach statistics."""
        if not events:
            return {"total": 0}

        total = len(events)
        sent = sum(1 for e in events if e.status != OutreachStatus.PENDING)
        opened = sum(
            1 for e in events
            if e.status in [OutreachStatus.OPENED, OutreachStatus.REPLIED]
        )
        replied = sum(1 for e in events if e.status == OutreachStatus.REPLIED)

        by_response = {}
        for e in events:
            if e.response_type:
                r = e.response_type.value
                by_response[r] = by_response.get(r, 0) + 1

        return {
            "total_events": total,
            "sent": sent,
            "opened": opened,
            "replied": replied,
            "open_rate": round(opened / sent * 100, 1) if sent else 0,
            "reply_rate": round(replied / sent * 100, 1) if sent else 0,
            "by_response_type": by_response,
            "by_step": {
                step: sum(1 for e in events if e.sequence_step == step)
                for step in range(1, 4)
            },
        }
