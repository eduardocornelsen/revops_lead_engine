# 🚀 B2B Autonomous Lead Engine & Automated SDR Pipeline

> **AI-Powered RevOps: Full-Cycle B2B Lead Intelligence & SDR Automation**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Business Problem

Most B2B sales teams burn **60–70% of SDR time** on manual prospecting, data entry, and qualification calls that go nowhere. Meanwhile, high-quality leads decay — response time kills conversion.

> *"Why does it take 3 days to reach a lead that filled out a form, and why are 40% of our outbound leads outside our ICP?"*

This project builds a **fully autonomous B2B sales pipeline** — from programmatic lead generation to AI-powered qualification to CRM-ready opportunities — eliminating manual SDR grunt work.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    B2B AUTONOMOUS LEAD ENGINE                                │
│                    Full-Cycle SDR Automation                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │  STAGE 1    │──▶│  STAGE 2     │──▶│  STAGE 3     │──▶│  STAGE 4     │    │
│  │ PROSPECTING │   │ ENRICHMENT   │   │ SCORING &    │   │ AUTOMATED    │    │
│  │ & DISCOVERY │   │ & PROFILING  │   │ QUALIFICATION│   │ SDR OUTREACH │    │
│  └─────────────┘   └──────────────┘   └──────────────┘   └──────┬───────┘    │
│        │                                                         │           │
│        ▼                                                         ▼           │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     STAGE 5: CRM SYNC & HANDOFF                     │     │
│  │              HubSpot / Salesforce — Opportunity Management          │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
ICP Config ──▶ Lead Discovery ──▶ Enrichment ──▶ Scoring ──▶ Outreach ──▶    CRM
  (YAML)      (Apollo/CNPJ)    (Hunter/BuiltWith)  (Rules/ML)   (Email)    (HubSpot)
                    │                   │               │           │           │
                    ▼                   ▼               ▼           ▼           ▼
               dim_companies    fct_enriched_leads  fct_scored  fct_outreach  Deals
               dim_contacts                         + deal_brief  _events    + Opps
```




```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA LINEAGE & PERSISTENCE                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│ ICP CONFIG  ──▶  DISCOVERY   ──▶  ENRICHMENT  ──▶   SCORING    ──▶   OUTREACH   ──▶   CRM      │
│   (YAML)       (Apollo/CNPJ)   (Hunter/BuiltWith)  (Rules/ML)        (Email)        (HubSpot)  │
│      │               │                │               │                 │              │       │
│      │         dim_companies   fct_enriched_leads  fct_scored     fct_outreach       Deals     │                  │      │         dim_contacts           │            + deal_brief     _events         + Opps     │
│      │               │                │               │                 │              │       │
│      ▼               ▼                ▼               ▼                 ▼              ▼       │
│┌───────────┐   ┌───────────┐    ┌───────────┐   ┌───────────┐    ┌───────────┐   ┌───────────┐ │
││  TARGETS  │   │ RAW LEADS │    │ PROFILES  │   │  SCORES   │    │ SEQUENCES │   │ DEALS/OPPS│ │
│└─────┬─────┘   └─────┬─────┘    └─────┬─────┘   └─────┬─────┘    └─────┬─────┘   └─────┬─────┘ │
│      └───────────────┴──────────┬─────┴───────────────┴─┬──────────────┴───────────────┘       │
│                                 ▼                       ▼                                      │
│                         LAKEHOUSE / WAREHOUSE (SQLite ⮕ BigQuery)                             │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Stage 1: Autonomous Lead Prospecting
- 🎯 **ICP-driven discovery** — declarative YAML config for Ideal Customer Profile
- 🇧🇷 **Brazil data** — Receita Federal (CNPJ), CNAE industry codes, public registries
- 🇺🇸 **US data** — Apollo.io, Crunchbase, SEC EDGAR integration interfaces
- 🔄 **Automated deduplication** against existing database

### Stage 2: Lead Enrichment & Profiling
- 👤 **Contact discovery** — find decision-makers (VP Sales, CRO, Head of RevOps)
- 🔍 **Tech stack detection** — identify CRM/analytics gaps for selling opportunities
- 📰 **Buying signals** — track funding rounds, exec hires, product launches
- 🔗 **Multi-source merge** — unified enriched lead profile

### Stage 3: Lead Scoring & Qualification
- 📊 **0–100 scoring model** — firmographic fit, behavioral signals, tech stack gaps
- ✅ **BANT pre-qualification** — Budget, Authority, Need, Timeline automated checks
- 🤖 **AI deal brief generator** — SPIN questions, call scripts, objection handling
- 🌐 **FastAPI scoring endpoint** — real-time lead scoring API

### Stage 4: Automated SDR Outreach
- 📧 **3-touch email sequences** — personalized with enrichment data
- 🏷️ **Response classification** — Interested / Not Now / Not Interested / Auto-reply
- 📅 **Meeting booking integration** — auto-send calendar links on positive reply

### Stage 5: CRM Sync & Handoff
- 🔄 **Bi-directional CRM sync** — HubSpot/Salesforce integration
- 🏢 **Auto-create records** — Company → Contact → Deal with full enrichment data
- 📈 **Full attribution** — lead source, enrichment sources, converting channel

---

## 🛠️ Tech Stack

| Layer             | Tools                                                              |
| ----------------- | ------------------------------------------------------------------ |
| **Languages**     | Python 3.11+ · SQL                                                 |
| **Data Models**   | Pydantic v2 · SQLite (MVP) / BigQuery (production)                 |
| **API**           | FastAPI · Uvicorn                                                  |
| **AI/ML**         | LLM prompt templates · Rule-based scoring (→ Scikit-learn/XGBoost) |
| **Automation**    | Python pipeline orchestrator (→ n8n/Airflow)                       |
| **CRM**           | HubSpot API interface (mock for MVP)                               |
| **Visualization** | Streamlit · Plotly                                                 |
| **Testing**       | pytest                                                             |
| **Config**        | YAML (ICP) · Pydantic Settings (env vars)                          |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or uv

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd lead_engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Full Pipeline

```bash
# Run the end-to-end pipeline (discovery → enrichment → scoring → outreach → CRM)
python -m src.pipeline
```

### Start the API Server

```bash
# Launch FastAPI scoring endpoint
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# API docs at http://localhost:8000/docs
```

### Launch the Dashboard

```bash
# Start Streamlit dashboard
streamlit run src/dashboard/app.py
```

---

## 📁 Project Structure

```
lead_engine/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata
├── config/
│   └── icp_config.yaml          # Ideal Customer Profile definition
├── docs/
│   ├── architecture.md          # System architecture (Mermaid diagrams)
│   └── data_dictionary.md       # Schema documentation
├── src/
│   ├── __init__.py
│   ├── pipeline.py              # End-to-end pipeline orchestrator
│   ├── config/
│   │   ├── settings.py          # Environment settings (Pydantic)
│   │   └── icp_loader.py        # ICP YAML config loader
│   ├── models/
│   │   └── models.py            # Pydantic data models
│   ├── database/
│   │   ├── database.py          # SQLite database manager
│   │   └── seed_data.py         # Sample data generator
│   ├── discovery/
│   │   └── discovery.py         # Lead discovery engine (Stage 1)
│   ├── enrichment/
│   │   └── enrichment.py        # Enrichment pipeline (Stage 2)
│   ├── scoring/
│   │   ├── scoring.py           # Lead scoring engine (Stage 3)
│   │   └── deal_brief.py        # AI deal brief generator
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── outreach/
│   │   └── outreach.py          # Outreach automation (Stage 4)
│   ├── crm/
│   │   └── crm_sync.py          # CRM sync (Stage 5)
│   └── dashboard/
│       └── app.py               # Streamlit dashboard
├── tests/
│   ├── test_icp_loader.py
│   ├── test_scoring.py
│   └── test_pipeline.py
├── deal_briefs/                 # Sample AI-generated deal briefs
├── notebooks/                   # EDA & model training notebooks
└── workflows/                   # n8n workflow exports
```

---

## 📊 Sample Deal Brief Output

```
═══════════════════════════════════════════════════════
DEAL BRIEF: Acme Corp (Score: 87/100)
═══════════════════════════════════════════════════════

COMPANY: Acme Corp | B2B SaaS | 150 employees | $12M ARR
CONTACT: Jane Smith, VP of Revenue Operations
SOURCE: Apollo.io + LinkedIn enrichment

BANT QUALIFICATION:
✅ Budget: Series B ($15M raised Q3 2025)
✅ Authority: VP-level, reports to CRO
✅ Need: Using legacy Sheets for pipeline tracking (no CRM detected)
⚠️ Timeline: No immediate buying signal, but hired 3 SDRs last month

SPIN DISCOVERY QUESTIONS:
[S] "How are you currently tracking pipeline velocity across your SDR team?"
[P] "What happens when a deal stalls at Stage 3 — how does your team surface that?"
[I] "If pipeline visibility takes 2 days to update, what does that cost per quarter?"
[N] "If you could see real-time conversion and auto-flag stalled deals, how would
     that change your Monday forecast meeting?"

OBJECTION PREP:
• "We already use Sheets" → "Sheets works until 50 deals/month — then manual
   updates become your bottleneck."
• "We're evaluating other tools" → "Happy to share how our approach reduces eval
   time by giving you a live proof-of-concept."
═══════════════════════════════════════════════════════
```

---

## 🗺️ Roadmap

### ✅ MVP (Current)
- [x] ICP-driven lead discovery with mock data
- [x] Multi-source enrichment pipeline (mock providers)
- [x] Rule-based lead scoring (0–100)
- [x] BANT pre-qualification
- [x] AI deal brief generation (prompt templates)
- [x] 3-touch email sequence templates
- [x] FastAPI scoring endpoint
- [x] Streamlit pipeline dashboard
- [x] Mock CRM sync (HubSpot interface)

### 🔜 Phase 2: Real Integrations
- [ ] Apollo.io API integration (200 free leads/month)
- [ ] Hunter.io email finder integration
- [ ] BuiltWith/Wappalyzer tech stack detection
- [ ] Receita Federal CNPJ API (Brazil)
- [ ] HubSpot CRM live sync

### 🔮 Phase 3: ML & Automation
- [ ] Scikit-learn/XGBoost lead scoring model
- [ ] MLFlow experiment tracking
- [ ] n8n workflow orchestration
- [ ] SendGrid email dispatch
- [ ] LLM-powered response classification
- [ ] Cal.com meeting booking integration

### 🏁 Phase 4: Production
- [ ] BigQuery/Snowflake data warehouse
- [ ] dbt transformation models
- [ ] Airflow DAG scheduling
- [ ] Salesforce integration
- [ ] Looker Studio exec dashboards

---

## 📖 Documentation

- [Architecture Guide](docs/architecture.md) — System design & data flow diagrams
- [Data Dictionary](docs/data_dictionary.md) — Schema documentation for all tables

---

## 🤝 Contributing

This project is part of a portfolio demonstrating end-to-end RevOps automation capabilities. Contributions welcome!

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
