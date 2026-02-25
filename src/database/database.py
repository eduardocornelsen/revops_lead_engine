"""
B2B Lead Engine — SQLite Database Manager

Handles all database operations: table creation, CRUD, and queries.
MVP uses SQLite; designed for easy migration to BigQuery/Snowflake.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.models.models import (
    Company,
    Contact,
    EnrichedLead,
    ScoredLead,
    OutreachEvent,
    QualificationStatus,
    OutreachChannel,
    OutreachStatus,
)


class Database:
    """SQLite database manager for the lead engine."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_tables(self):
        """Create all pipeline tables."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS dim_companies (
                    company_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    industry TEXT DEFAULT '',
                    country TEXT DEFAULT '',
                    state TEXT DEFAULT '',
                    employee_count INTEGER DEFAULT 0,
                    revenue_usd REAL DEFAULT 0.0,
                    website TEXT DEFAULT '',
                    tech_stack TEXT DEFAULT '[]',
                    funding_stage TEXT DEFAULT '',
                    founded_year INTEGER,
                    cnpj TEXT,
                    cnae_code TEXT,
                    source TEXT DEFAULT 'manual',
                    discovered_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dim_contacts (
                    contact_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL REFERENCES dim_companies(company_id),
                    full_name TEXT NOT NULL,
                    title TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    linkedin_url TEXT DEFAULT '',
                    seniority TEXT DEFAULT '',
                    department TEXT DEFAULT '',
                    source TEXT DEFAULT 'manual',
                    verified INTEGER DEFAULT 0,
                    discovered_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS fct_enriched_leads (
                    lead_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL REFERENCES dim_companies(company_id),
                    contact_id TEXT NOT NULL REFERENCES dim_contacts(contact_id),
                    tech_stack_detected TEXT DEFAULT '[]',
                    tech_stack_gaps TEXT DEFAULT '[]',
                    buying_signals TEXT DEFAULT '[]',
                    social_signals TEXT DEFAULT '{}',
                    news_mentions TEXT DEFAULT '[]',
                    enrichment_completeness REAL DEFAULT 0.0,
                    enrichment_sources TEXT DEFAULT '[]',
                    enriched_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS fct_scored_leads (
                    lead_id TEXT PRIMARY KEY REFERENCES fct_enriched_leads(lead_id),
                    score REAL DEFAULT 0.0,
                    score_breakdown TEXT DEFAULT '{}',
                    qualification_status TEXT DEFAULT 'disqualified',
                    budget_signal INTEGER DEFAULT 0,
                    authority_signal INTEGER DEFAULT 0,
                    need_signal INTEGER DEFAULT 0,
                    timeline_signal INTEGER DEFAULT 0,
                    deal_brief TEXT DEFAULT '',
                    deal_stage TEXT DEFAULT '',
                    scored_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS fct_outreach_events (
                    event_id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL REFERENCES fct_scored_leads(lead_id),
                    channel TEXT DEFAULT 'email',
                    sequence_step INTEGER DEFAULT 1,
                    subject TEXT DEFAULT '',
                    body TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    response_type TEXT,
                    sent_at TEXT,
                    opened_at TEXT,
                    responded_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_contacts_company ON dim_contacts(company_id);
                CREATE INDEX IF NOT EXISTS idx_enriched_company ON fct_enriched_leads(company_id);
                CREATE INDEX IF NOT EXISTS idx_scored_status ON fct_scored_leads(qualification_status);
                CREATE INDEX IF NOT EXISTS idx_outreach_lead ON fct_outreach_events(lead_id);
            """)

    # ── Companies ──────────────────────────────────────

    def insert_company(self, company: Company) -> str:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO dim_companies
                   (company_id, name, industry, country, state, employee_count,
                    revenue_usd, website, tech_stack, funding_stage, founded_year,
                    cnpj, cnae_code, source, discovered_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    company.company_id, company.name, company.industry,
                    company.country, company.state, company.employee_count,
                    company.revenue_usd, company.website, company.tech_stack_json,
                    company.funding_stage, company.founded_year,
                    company.cnpj, company.cnae_code,
                    company.source, company.discovered_at.isoformat(),
                ),
            )
        return company.company_id

    def get_companies(self, limit: int = 100) -> list[Company]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM dim_companies ORDER BY discovered_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_company(r) for r in rows]

    def get_company(self, company_id: str) -> Optional[Company]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM dim_companies WHERE company_id = ?", (company_id,)
            ).fetchone()
        return self._row_to_company(row) if row else None

    def _row_to_company(self, row: sqlite3.Row) -> Company:
        d = dict(row)
        d["tech_stack"] = json.loads(d.get("tech_stack", "[]"))
        d["discovered_at"] = datetime.fromisoformat(d["discovered_at"])
        return Company(**d)

    # ── Contacts ───────────────────────────────────────

    def insert_contact(self, contact: Contact) -> str:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO dim_contacts
                   (contact_id, company_id, full_name, title, email, phone,
                    linkedin_url, seniority, department, source, verified, discovered_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    contact.contact_id, contact.company_id, contact.full_name,
                    contact.title, contact.email, contact.phone,
                    contact.linkedin_url, contact.seniority, contact.department,
                    contact.source, int(contact.verified),
                    contact.discovered_at.isoformat(),
                ),
            )
        return contact.contact_id

    def get_contacts(self, company_id: Optional[str] = None, limit: int = 100) -> list[Contact]:
        with self._connect() as conn:
            if company_id:
                rows = conn.execute(
                    "SELECT * FROM dim_contacts WHERE company_id = ? LIMIT ?",
                    (company_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM dim_contacts ORDER BY discovered_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [self._row_to_contact(r) for r in rows]

    def _row_to_contact(self, row: sqlite3.Row) -> Contact:
        d = dict(row)
        d["verified"] = bool(d.get("verified", 0))
        d["discovered_at"] = datetime.fromisoformat(d["discovered_at"])
        return Contact(**d)

    # ── Enriched Leads ─────────────────────────────────

    def insert_enriched_lead(self, lead: EnrichedLead) -> str:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fct_enriched_leads
                   (lead_id, company_id, contact_id, tech_stack_detected, tech_stack_gaps,
                    buying_signals, social_signals, news_mentions,
                    enrichment_completeness, enrichment_sources, enriched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lead.lead_id, lead.company_id, lead.contact_id,
                    json.dumps(lead.tech_stack_detected),
                    json.dumps(lead.tech_stack_gaps),
                    json.dumps(lead.buying_signals),
                    json.dumps(lead.social_signals),
                    json.dumps(lead.news_mentions),
                    lead.enrichment_completeness,
                    json.dumps(lead.enrichment_sources),
                    lead.enriched_at.isoformat(),
                ),
            )
        return lead.lead_id

    def get_enriched_leads(self, limit: int = 100) -> list[EnrichedLead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM fct_enriched_leads ORDER BY enriched_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_enriched_lead(r) for r in rows]

    def _row_to_enriched_lead(self, row: sqlite3.Row) -> EnrichedLead:
        d = dict(row)
        for field in ["tech_stack_detected", "tech_stack_gaps", "buying_signals",
                       "news_mentions", "enrichment_sources"]:
            d[field] = json.loads(d.get(field, "[]"))
        d["social_signals"] = json.loads(d.get("social_signals", "{}"))
        d["enriched_at"] = datetime.fromisoformat(d["enriched_at"])
        return EnrichedLead(**d)

    # ── Scored Leads ───────────────────────────────────

    def insert_scored_lead(self, lead: ScoredLead) -> str:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fct_scored_leads
                   (lead_id, score, score_breakdown, qualification_status,
                    budget_signal, authority_signal, need_signal, timeline_signal,
                    deal_brief, deal_stage, scored_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lead.lead_id, lead.score,
                    lead.score_breakdown.model_dump_json(),
                    lead.qualification_status.value,
                    int(lead.budget_signal), int(lead.authority_signal),
                    int(lead.need_signal), int(lead.timeline_signal),
                    lead.deal_brief, lead.deal_stage,
                    lead.scored_at.isoformat(),
                ),
            )
        return lead.lead_id

    def get_scored_leads(
        self, status: Optional[str] = None, limit: int = 100
    ) -> list[ScoredLead]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """SELECT * FROM fct_scored_leads
                       WHERE qualification_status = ? ORDER BY score DESC LIMIT ?""",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM fct_scored_leads ORDER BY score DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [self._row_to_scored_lead(r) for r in rows]

    def _row_to_scored_lead(self, row: sqlite3.Row) -> ScoredLead:
        d = dict(row)
        from src.models.models import ScoreBreakdown
        d["score_breakdown"] = ScoreBreakdown(**json.loads(d.get("score_breakdown", "{}")))
        d["qualification_status"] = QualificationStatus(d["qualification_status"])
        d["budget_signal"] = bool(d.get("budget_signal", 0))
        d["authority_signal"] = bool(d.get("authority_signal", 0))
        d["need_signal"] = bool(d.get("need_signal", 0))
        d["timeline_signal"] = bool(d.get("timeline_signal", 0))
        d["scored_at"] = datetime.fromisoformat(d["scored_at"])
        return ScoredLead(**d)

    # ── Outreach Events ────────────────────────────────

    def insert_outreach_event(self, event: OutreachEvent) -> str:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fct_outreach_events
                   (event_id, lead_id, channel, sequence_step, subject, body,
                    status, response_type, sent_at, opened_at, responded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.event_id, event.lead_id, event.channel.value,
                    event.sequence_step, event.subject, event.body,
                    event.status.value,
                    event.response_type.value if event.response_type else None,
                    event.sent_at.isoformat() if event.sent_at else None,
                    event.opened_at.isoformat() if event.opened_at else None,
                    event.responded_at.isoformat() if event.responded_at else None,
                ),
            )
        return event.event_id

    def get_outreach_events(self, lead_id: Optional[str] = None, limit: int = 100) -> list[OutreachEvent]:
        with self._connect() as conn:
            if lead_id:
                rows = conn.execute(
                    "SELECT * FROM fct_outreach_events WHERE lead_id = ? LIMIT ?",
                    (lead_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM fct_outreach_events ORDER BY sent_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [self._row_to_outreach_event(r) for r in rows]

    def _row_to_outreach_event(self, row: sqlite3.Row) -> OutreachEvent:
        d = dict(row)
        d["channel"] = OutreachChannel(d.get("channel", "email"))
        d["status"] = OutreachStatus(d.get("status", "pending"))
        if d.get("response_type"):
            from src.models.models import ResponseType
            d["response_type"] = ResponseType(d["response_type"])
        for dt_field in ["sent_at", "opened_at", "responded_at"]:
            if d.get(dt_field):
                d[dt_field] = datetime.fromisoformat(d[dt_field])
        return OutreachEvent(**d)

    # ── Stats ──────────────────────────────────────────

    def get_pipeline_stats(self) -> dict:
        """Get aggregate stats across all tables with funnel metrics."""
        with self._connect() as conn:
            stats = {}
            for table in ["dim_companies", "dim_contacts", "fct_enriched_leads",
                          "fct_scored_leads", "fct_outreach_events"]:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count

            # Qualification breakdown
            rows = conn.execute(
                """SELECT qualification_status, COUNT(*) as cnt
                   FROM fct_scored_leads GROUP BY qualification_status"""
            ).fetchall()
            stats["qualification_breakdown"] = {r["qualification_status"]: r["cnt"] for r in rows}

            # Average score
            avg = conn.execute(
                "SELECT AVG(score) as avg_score FROM fct_scored_leads"
            ).fetchone()
            stats["avg_score"] = round(avg["avg_score"], 1) if avg["avg_score"] else 0

            # Funnel: tracked at LEAD (contact) level for consistent decrease
            # Total contacts in the pool
            stats["funnel_pool"] = stats["dim_contacts"]

            # Contacts whose company has an enriched lead (= ICP matched + enrichment success)
            icp_contacts = conn.execute(
                """SELECT COUNT(DISTINCT ct.contact_id) FROM dim_contacts ct
                   JOIN dim_companies c ON ct.company_id = c.company_id
                   WHERE c.company_id IN (SELECT DISTINCT company_id FROM fct_enriched_leads)"""
            ).fetchone()[0]
            stats["funnel_icp_contacts"] = icp_contacts

            # Enriched leads
            stats["funnel_enriched"] = stats["fct_enriched_leads"]

            # Scored leads
            stats["funnel_scored"] = stats["fct_scored_leads"]

            # Qualified (hot) leads
            qualified_leads = conn.execute(
                "SELECT COUNT(*) FROM fct_scored_leads WHERE qualification_status = 'qualified'"
            ).fetchone()[0]
            stats["funnel_qualified"] = qualified_leads

            # Qualified + Nurture (pipeline)
            pipeline_leads = conn.execute(
                "SELECT COUNT(*) FROM fct_scored_leads WHERE qualification_status IN ('qualified','nurture')"
            ).fetchone()[0]
            stats["funnel_pipeline"] = pipeline_leads

            # Unique companies at qualified level (for funnel_qualified_companies)
            qualified_companies = conn.execute(
                """SELECT COUNT(DISTINCT e.company_id)
                   FROM fct_scored_leads s
                   JOIN fct_enriched_leads e ON s.lead_id = e.lead_id
                   WHERE s.qualification_status = 'qualified'"""
            ).fetchone()[0]
            stats["funnel_qualified_companies"] = qualified_companies

            # Total pipeline value
            pipeline_val = conn.execute(
                """SELECT SUM(s.score * c.revenue_usd / 10000) as val
                   FROM fct_scored_leads s
                   JOIN fct_enriched_leads e ON s.lead_id = e.lead_id
                   JOIN dim_companies c ON e.company_id = c.company_id
                   WHERE s.qualification_status IN ('qualified', 'nurture')"""
            ).fetchone()
            stats["total_pipeline_value"] = round(pipeline_val[0], 2) if pipeline_val[0] else 0

            # Industry breakdown
            rows = conn.execute(
                "SELECT industry, COUNT(*) as cnt FROM dim_companies GROUP BY industry ORDER BY cnt DESC"
            ).fetchall()
            stats["industry_breakdown"] = {r["industry"]: r["cnt"] for r in rows}

            # Market breakdown
            rows = conn.execute(
                "SELECT country, COUNT(*) as cnt FROM dim_companies GROUP BY country ORDER BY cnt DESC"
            ).fetchall()
            stats["market_breakdown"] = {r["country"]: r["cnt"] for r in rows}

            # Outreach stats
            total_sent = conn.execute(
                "SELECT COUNT(*) FROM fct_outreach_events WHERE status != 'pending'"
            ).fetchone()[0]
            total_opened = conn.execute(
                "SELECT COUNT(*) FROM fct_outreach_events WHERE opened_at IS NOT NULL"
            ).fetchone()[0]
            total_replied = conn.execute(
                "SELECT COUNT(*) FROM fct_outreach_events WHERE responded_at IS NOT NULL"
            ).fetchone()[0]
            total_interested = conn.execute(
                "SELECT COUNT(*) FROM fct_outreach_events WHERE response_type = 'interested'"
            ).fetchone()[0]
            stats["outreach_sent"] = total_sent
            stats["outreach_opened"] = total_opened
            stats["outreach_replied"] = total_replied
            stats["outreach_interested"] = total_interested

        return stats

    # ── Search & Filter ───────────────────────────────

    def search_leads(
        self,
        text_query: str = "",
        markets: list[str] | None = None,
        industries: list[str] | None = None,
        revenue_min: float | None = None,
        revenue_max: float | None = None,
        employees_min: int | None = None,
        employees_max: int | None = None,
        score_min: float | None = None,
        score_max: float | None = None,
        statuses: list[str] | None = None,
        seniorities: list[str] | None = None,
        sources: list[str] | None = None,
        bant_budget: bool | None = None,
        bant_authority: bool | None = None,
        bant_need: bool | None = None,
        bant_timeline: bool | None = None,
        limit: int = 200,
    ) -> list[dict]:
        """
        Search leads with dynamic filtering across all tables.

        Returns joined records: company + contact + enrichment + score data.
        """
        conditions = []
        params = []

        # Text search across company name, contact name, industry
        if text_query:
            conditions.append(
                "(c.name LIKE ? OR ct.full_name LIKE ? OR c.industry LIKE ? OR ct.title LIKE ?)"
            )
            q = f"%{text_query}%"
            params.extend([q, q, q, q])

        # Market filter
        if markets:
            placeholders = ",".join("?" * len(markets))
            conditions.append(f"c.country IN ({placeholders})")
            params.extend(markets)

        # Industry filter
        if industries:
            placeholders = ",".join("?" * len(industries))
            conditions.append(f"c.industry IN ({placeholders})")
            params.extend(industries)

        # Revenue range
        if revenue_min is not None:
            conditions.append("c.revenue_usd >= ?")
            params.append(revenue_min)
        if revenue_max is not None:
            conditions.append("c.revenue_usd <= ?")
            params.append(revenue_max)

        # Employee range
        if employees_min is not None:
            conditions.append("c.employee_count >= ?")
            params.append(employees_min)
        if employees_max is not None:
            conditions.append("c.employee_count <= ?")
            params.append(employees_max)

        # Score range
        if score_min is not None:
            conditions.append("s.score >= ?")
            params.append(score_min)
        if score_max is not None:
            conditions.append("s.score <= ?")
            params.append(score_max)

        # Status filter
        if statuses:
            placeholders = ",".join("?" * len(statuses))
            conditions.append(f"s.qualification_status IN ({placeholders})")
            params.extend(statuses)

        # Seniority filter
        if seniorities:
            placeholders = ",".join("?" * len(seniorities))
            conditions.append(f"ct.seniority IN ({placeholders})")
            params.extend(seniorities)

        # Source filter
        if sources:
            placeholders = ",".join("?" * len(sources))
            conditions.append(f"c.source IN ({placeholders})")
            params.extend(sources)

        # BANT filters
        if bant_budget is not None:
            conditions.append(f"s.budget_signal = ?")
            params.append(int(bant_budget))
        if bant_authority is not None:
            conditions.append(f"s.authority_signal = ?")
            params.append(int(bant_authority))
        if bant_need is not None:
            conditions.append(f"s.need_signal = ?")
            params.append(int(bant_need))
        if bant_timeline is not None:
            conditions.append(f"s.timeline_signal = ?")
            params.append(int(bant_timeline))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                s.lead_id, s.score, s.qualification_status, s.deal_stage,
                s.budget_signal, s.authority_signal, s.need_signal, s.timeline_signal,
                s.deal_brief,
                c.company_id, c.name as company_name, c.industry, c.country, c.state,
                c.employee_count, c.revenue_usd, c.website, c.tech_stack,
                c.funding_stage, c.source as company_source,
                ct.contact_id, ct.full_name as contact_name, ct.title as contact_title,
                ct.email, ct.phone, ct.linkedin_url, ct.seniority, ct.department,
                e.tech_stack_detected, e.tech_stack_gaps, e.buying_signals,
                e.social_signals, e.news_mentions, e.enrichment_completeness,
                e.enrichment_sources
            FROM fct_scored_leads s
            JOIN fct_enriched_leads e ON s.lead_id = e.lead_id
            JOIN dim_companies c ON e.company_id = c.company_id
            JOIN dim_contacts ct ON e.contact_id = ct.contact_id
            WHERE {where_clause}
            ORDER BY s.score DESC
            LIMIT ?
        """
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        results = []
        for row in rows:
            d = dict(row)
            # Parse JSON fields
            for field in ["tech_stack", "tech_stack_detected", "tech_stack_gaps",
                          "buying_signals", "news_mentions", "enrichment_sources"]:
                if d.get(field):
                    d[field] = json.loads(d[field])
            if d.get("social_signals"):
                d["social_signals"] = json.loads(d["social_signals"])
            d["budget_signal"] = bool(d.get("budget_signal", 0))
            d["authority_signal"] = bool(d.get("authority_signal", 0))
            d["need_signal"] = bool(d.get("need_signal", 0))
            d["timeline_signal"] = bool(d.get("timeline_signal", 0))
            results.append(d)

        return results

    def get_lead_detail(self, lead_id: str) -> dict | None:
        """Get full lead detail joining all tables + outreach events."""
        leads = self.search_leads(limit=1000)
        lead = next((l for l in leads if l["lead_id"] == lead_id), None)
        if not lead:
            return None

        # Add outreach events
        events = self.get_outreach_events(lead_id=lead_id, limit=50)
        lead["outreach_events"] = [
            {
                "event_id": e.event_id,
                "channel": e.channel.value,
                "sequence_step": e.sequence_step,
                "subject": e.subject,
                "body": e.body,
                "status": e.status.value,
                "response_type": e.response_type.value if e.response_type else None,
                "sent_at": e.sent_at.isoformat() if e.sent_at else None,
                "opened_at": e.opened_at.isoformat() if e.opened_at else None,
                "responded_at": e.responded_at.isoformat() if e.responded_at else None,
            }
            for e in events
        ]

        return lead

    def get_unique_values(self, column: str, table: str) -> list[str]:
        """Get unique values for a column (for filter dropdowns)."""
        allowed = {
            "country": "dim_companies",
            "industry": "dim_companies",
            "source": "dim_companies",
            "seniority": "dim_contacts",
            "department": "dim_contacts",
            "funding_stage": "dim_companies",
        }
        if column not in allowed or allowed[column] != table:
            return []

        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT DISTINCT {column} FROM {table} WHERE {column} != '' ORDER BY {column}"
            ).fetchall()
        return [r[0] for r in rows]
