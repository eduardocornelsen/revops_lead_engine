"""
B2B Lead Engine — FastAPI Application

REST API for lead scoring, listing, and deal brief retrieval.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.config.settings import settings
from src.config.icp_loader import load_icp_config
from src.database.database import Database
from src.models.models import QualificationStatus


# ── Shared State ──────────────────────────────────────

_db: Optional[Database] = None
_icp_config = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    global _db, _icp_config
    _db = Database(settings.database_path)
    _icp_config = load_icp_config(settings.icp_config_path)
    yield


# ── App Instance ──────────────────────────────────────

app = FastAPI(
    title="B2B Lead Engine API",
    description="Lead scoring, qualification, and deal brief generation for B2B sales pipelines.",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Response Models ───────────────────────────────────

class CompanyResponse(BaseModel):
    company_id: str
    name: str
    industry: str
    country: str
    state: str
    employee_count: int
    revenue_usd: float
    website: str
    tech_stack: list[str]
    funding_stage: str
    source: str


class ScoredLeadResponse(BaseModel):
    lead_id: str
    score: float
    qualification_status: str
    budget_signal: bool
    authority_signal: bool
    need_signal: bool
    timeline_signal: bool
    deal_stage: str


class PipelineStatsResponse(BaseModel):
    dim_companies: int
    dim_contacts: int
    fct_enriched_leads: int
    fct_scored_leads: int
    fct_outreach_events: int
    avg_score: float
    qualification_breakdown: dict


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


# ── Endpoints ─────────────────────────────────────────

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        database="connected" if _db else "disconnected",
    )


@app.get("/companies", response_model=list[CompanyResponse])
async def list_companies(
    limit: int = Query(default=50, le=500),
):
    """List discovered companies."""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not initialized")

    companies = _db.get_companies(limit=limit)
    return [
        CompanyResponse(
            company_id=c.company_id,
            name=c.name,
            industry=c.industry,
            country=c.country,
            state=c.state,
            employee_count=c.employee_count,
            revenue_usd=c.revenue_usd,
            website=c.website,
            tech_stack=c.tech_stack,
            funding_stage=c.funding_stage,
            source=c.source,
        )
        for c in companies
    ]


@app.get("/leads", response_model=list[ScoredLeadResponse])
async def list_scored_leads(
    status: Optional[str] = Query(default=None, description="Filter by status: qualified, nurture, disqualified"),
    limit: int = Query(default=50, le=500),
):
    """List scored leads with optional status filter."""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not initialized")

    leads = _db.get_scored_leads(status=status, limit=limit)
    return [
        ScoredLeadResponse(
            lead_id=l.lead_id,
            score=l.score,
            qualification_status=l.qualification_status.value,
            budget_signal=l.budget_signal,
            authority_signal=l.authority_signal,
            need_signal=l.need_signal,
            timeline_signal=l.timeline_signal,
            deal_stage=l.deal_stage,
        )
        for l in leads
    ]


@app.get("/leads/{lead_id}/brief")
async def get_deal_brief(lead_id: str):
    """Get the deal brief for a specific lead."""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not initialized")

    leads = _db.get_scored_leads(limit=500)
    lead = next((l for l in leads if l.lead_id == lead_id), None)

    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

    return {
        "lead_id": lead.lead_id,
        "score": lead.score,
        "deal_brief": lead.deal_brief,
        "deal_stage": lead.deal_stage,
    }


@app.get("/stats", response_model=PipelineStatsResponse)
async def pipeline_stats():
    """Get aggregate pipeline statistics."""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not initialized")

    stats = _db.get_pipeline_stats()
    return PipelineStatsResponse(**stats)
