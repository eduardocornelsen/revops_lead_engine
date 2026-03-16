<p align="center">
  <h1 align="center">🚀 RevOps Lead Engine</h1>
  <p align="center">
    <strong>AI-Powered B2B Revenue Operations Command Center</strong><br/>
    Full-cycle autonomous lead generation · Predictive scenario modeling · Post-sales retention analytics
  </p>
  <p align="center">
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
    <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/></a>
    <a href="https://plotly.com"><img src="https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/></a>
    <a href="https://docs.pydantic.dev"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic"/></a>
    <a href="#license"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/></a>
  </p>

<a href="https://revops-lead-engine.streamlit.app/">
  <img src="https://raw.githubusercontent.com/eduardocornelsen/revops_lead_engine/main/docs/images/cover-small.jpg" width="100%" alt="RevOps Lead Engine Dashboard" style="border-radius: 8px;">
</a>
<br><br>

  <p align="center">
    <a href="https://revops-lead-engine.streamlit.app/"><img src="https://img.shields.io/badge/🚀_LIVE_DEMO-Click_to_Launch-ff4b4b?style=for-the-badge&logoColor=white" alt="Live Demo"/></a>
  </p>
</p>

---

## 📋 The Problem

Most B2B sales teams burn **60–70% of SDR time** on manual prospecting, data entry, and qualification calls that go nowhere. Meanwhile, high-quality leads decay — response time kills conversion.

> *"Why does it take 3 days to reach a lead that filled out a form, and why are 40% of our outbound leads outside our ICP?"*

**RevOps Lead Engine** solves this by building a fully autonomous B2B sales pipeline — from programmatic lead generation to AI-powered qualification, predictive revenue modeling, and post-sales retention tracking — eliminating manual SDR grunt work and giving leadership real-time pipeline visibility.

---

## ✨ Key Features

### 💬 AI RevOps Copilot
A GenAI conversational interface embedded directly inside the dashboard. Ask natural-language questions about pipeline risk, quota pacing, rep performance, and revenue forecasts. Includes quick-action executive prompts for CEO, VP Sales, and VP Revenue personas.

### 🔮 Revenue Scenario Modeler
An interactive predictive engine with four adjustable levers — Lead Volume, Win Rate, ACV, and Cycle Time. Projects a 90-day S-curve revenue trajectory with real-time AI insights that tell you whether you'll hit quota and why.

### 🏦 Post-Sales & Expansion (NDR)
Tracks the "BowTie Funnel" beyond closed-won. Features Net Dollar Retention (NDR) metrics, Gross Retention Rate, Account Health scoring across 3 risk tiers, and a dynamic ARR Composition Waterfall chart (Starting ARR → New Logos → Expansion → Contraction → Churn → Ending ARR).

### 🧠 Explainable AI Lead Scoring (XAI)
Every lead score (0–100) includes transparent textual explanations: `(+25 ICP) Strong revenue fit`, `(-30 Needs) Enterprise lock-in risk`. Hover over any lead to see the full scoring breakdown — no black-box models.

### 📊 Revenue Dashboard
VP-level executive overview tracking Quota Attainment, Pipeline Coverage Ratio, Average Deal Size, Win Rate trends, CAC/LTV unit economics, and real-time SDR pacing metrics — all filterable by date range and individual sales rep.

### ⚡ Lead Generation Engine
Filter the entire database by firmographic fit (industry, geography, employee count, revenue) and BANT qualification signals. Queue leads into targeted outreach campaigns with one click.

### 🔍 Lead Intelligence & Search
Full-text search across the active lead database with XAI tooltips explaining every score component. Instantly surface high-intent prospects with technology stack gaps and recent buying signals.

### 🧭 Sales Navigator
Deep-dive into individual leads with AI-generated Deal Briefs, SPIN discovery questions, BANT qualification summaries, and one-click actions for LinkedIn outreach and company research.

### 📈 Pipeline Analytics
Conversion funnel visualization, Stage Velocity tracking (days per pipeline stage), Campaign ROI attribution table, and an SDR Leaderboard ranking reps by pipeline generated, meetings booked, and quota attainment.

### 📧 Outreach Performance
Tracks 3-touch email cadence performance — opens, replies, bounces — with weekly trend charts and response classification (Interested / Not Now / Not Interested / Auto-reply).

### 💼 CRM / Salesforce View
Simulated Salesforce-style opportunity management with deal stages, amounts, close dates, and pipeline progression tracking.

---

## 🏗️ System Architecture

```text
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
│        │                                                        │            │
│        ▼                                                        ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     STAGE 5: CRM SYNC & HANDOFF                     │     │
│  │              HubSpot / Salesforce — Opportunity Management          │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │               🖥️ STREAMLIT REVOPS COMMAND CENTER                    │     │
│  │  Revenue Dashboard · Scenario Modeler · AI Copilot · NDR Tracking   │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Data Lineage & Persistence

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA LINEAGE & PERSISTENCE                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│ ICP CONFIG  ──▶  DISCOVERY   ──▶  ENRICHMENT  ──▶   SCORING    ──▶   OUTREACH   ──▶   CRM      │
│   (YAML)       (Apollo/CNPJ)   (Hunter/BuiltWith)  (Rules/ML)        (Email)        (HubSpot)  │
│      │               │                │               │                 │              │       │
│      │         dim_companies   fct_enriched_leads  fct_scored     fct_outreach       Deals     │                                     │      │         dim_contacts           │            + deal_brief     _events         + Opps     │
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

## 🛠️ Tech Stack

| Layer               | Technology                                                                |
| ------------------- | ------------------------------------------------------------------------- |
| **Frontend**        | Streamlit, Custom CSS (Cybermorphic dark theme), Plotly Graph Objects     |
| **Backend**         | Python 3.10+ · SQLite3                                                    |
| **Data Models**     | Pydantic v2 (strict validation, JSON serialization)                       |
| **AI / ML**         | LLM prompt templates · Rule-based scoring engine · XAI transparency layer |
| **Data Simulation** | Faker · Random weighted distributions · Monte Carlo projections           |
| **API**             | FastAPI · Uvicorn (scoring endpoint)                                      |
| **CRM**             | HubSpot / Salesforce interface (mock for MVP)                             |
| **Testing**         | pytest                                                                    |
| **Config**          | YAML (ICP profiles) · `.streamlit/config.toml` (theme)                    |

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+ (Conda recommended)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/eduardocornelsen/revops_lead_engine.git
cd revops_lead_engine

# Create and activate conda environment
conda create -n lead_engine python=3.10 -y
conda activate lead_engine

# Install dependencies
pip install -r requirements.txt
```

### Generate the Pipeline Data

```bash
# Runs end-to-end: discovery → enrichment → scoring → outreach → CRM sync
python -m src.pipeline
```

### Launch the Command Center

```bash
streamlit run src/dashboard/app.py
# Open http://localhost:8501
```

### Start the API Server (Optional)

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
# Docs at http://localhost:8000/docs
```

---

## 📁 Project Structure

```text
revops_lead_engine/
├── .streamlit/
│   └── config.toml              # Streamlit theme configuration
├── config/
│   └── icp_config.yaml          # Ideal Customer Profile definition
├── docs/
│   ├── architecture.md          # System architecture diagrams
│   ├── data_dictionary.md       # Schema documentation for all tables
│   └── Real_Data_Integration_Guide.md  # Production API integration guide
├── src/
│   ├── pipeline.py              # End-to-end pipeline orchestrator
│   ├── config/
│   │   ├── settings.py          # Environment settings (Pydantic)
│   │   └── icp_loader.py        # ICP YAML config loader
│   ├── models/
│   │   └── models.py            # Pydantic data models (Company, Lead, Deal)
│   ├── database/
│   │   ├── database.py          # SQLite database engine & queries
│   │   └── seed_data.py         # Synthetic data generator
│   ├── discovery/
│   │   └── discovery.py         # Lead discovery engine (Stage 1)
│   ├── enrichment/
│   │   └── enrichment.py        # Multi-source enrichment pipeline (Stage 2)
│   ├── scoring/
│   │   ├── scoring.py           # Lead scoring engine with XAI (Stage 3)
│   │   └── deal_brief.py        # AI deal brief & SPIN question generator
│   ├── api/
│   │   └── main.py              # FastAPI scoring endpoint
│   ├── outreach/
│   │   └── outreach.py          # 3-touch email outreach automation (Stage 4)
│   ├── crm/
│   │   └── crm_sync.py          # CRM sync & handoff logic (Stage 5)
│   └── dashboard/
│       ├── app.py               # Main Streamlit application (1300+ lines)
│       └── sim_metrics.py       # Revenue simulation & metric generators
├── tests/
│   ├── test_icp_loader.py       # ICP config validation tests
│   ├── test_scoring.py          # Scoring engine unit tests
│   └── test_pipeline.py         # Pipeline integration tests
├── deal_briefs/                 # Sample AI-generated deal briefs
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata
└── README.md                    # This file
```

---

## 📊 Dashboard Modules

| #   | Module                 | Purpose                                                                                |
| --- | ---------------------- | -------------------------------------------------------------------------------------- |
| 1   | 💬 AI RevOps Copilot    | Natural-language AI chat for pipeline risk analysis, quota pacing, and rep performance |
| 2   | 📊 Revenue Dashboard    | VP-level KPIs: quota attainment, pipeline coverage, CAC/LTV, revenue forecast          |
| 3   | ⚡ Generate Leads       | Firmographic & BANT filtering engine to queue targeted outreach campaigns              |
| 4   | 🔍 Lead Intelligence    | Full-text search with XAI tooltips explaining score components                         |
| 5   | 🧭 Sales Navigator      | Individual lead deep-dive with AI Deal Briefs, SPIN questions, LinkedIn actions        |
| 6   | 💼 CRM / Salesforce     | Opportunity management with deal stages and pipeline progression                       |
| 7   | 📈 Pipeline Analytics   | Funnel drop-off, Stage Velocity, Campaign ROI attribution, SDR Leaderboard             |
| 8   | 📧 Outreach Performance | Email cadence tracking: opens, replies, bounces, response classification               |
| 9   | 🏦 Post-Sales (NDR)     | Net Dollar Retention, Account Health tiers, ARR Waterfall chart                        |
| 10  | 🔮 Scenario Modeler     | 90-day revenue trajectory projection with adjustable revenue levers and AI insights    |

---

## 🎨 Design Philosophy

The dashboard follows a **Cybermorphic** design language — a dark-mode aesthetic combining:

- **Deep gradient backgrounds** (`#020617` → `#1e3a8a`) for a premium, immersive feel
- **Glassmorphism metric cards** with `backdrop-filter: blur(16px)` and subtle border highlights
- **Staggered `@keyframes` load animations** for a polished entry experience
- **Neon accent colors** (indigo, emerald, cyan) against the dark canvas for data emphasis
- **High-contrast Plotly charts** with dark text on colored surfaces for maximum readability

---

## 🗺️ Roadmap

### ✅ Completed (v3.0)
- [x] 10-module Streamlit RevOps Command Center
- [x] ICP-driven lead discovery with simulated multi-source data
- [x] Multi-source enrichment pipeline (tech stack, buying signals)
- [x] Rule-based lead scoring (0–100) with XAI transparency
- [x] BANT pre-qualification automation
- [x] AI deal brief generation (SPIN questions, objection handling)
- [x] 3-touch email sequence engine with response classification
- [x] Revenue Scenario Modeler with 90-day S-curve projections
- [x] Post-Sales NDR module (Account Health, ARR Waterfall)
- [x] GenAI RevOps Copilot with executive prompt templates
- [x] FastAPI real-time scoring endpoint
- [x] Dynamic per-rep and per-period filtering across all modules
- [x] Cybermorphic dark-mode UI with CSS animations

### 🔜 Next Phase
- [ ] Apollo.io & Hunter.io live API integration
- [ ] HubSpot / Salesforce bi-directional CRM sync
- [ ] ML-based scoring model (XGBoost / Scikit-learn)
- [ ] MLFlow experiment tracking
- [ ] SendGrid email dispatch integration
- [ ] n8n / Airflow workflow orchestration
- [ ] BigQuery / Snowflake data warehouse migration

---

## 🔌 Production Integration

This project is powered by `src/pipeline.py` to generate realistic synthetic data for demonstration purposes without requiring expensive API keys.

To adapt this for a live production B2B SaaS environment, refer to:
👉 [Real Data Integration Guide](docs/Real_Data_Integration_Guide.md)

---

  ## 📖 Documentation
  
  | Document                                                           | Description                             |
  | ------------------------------------------------------------------ | --------------------------------------- |
  | [Architecture Guide](docs/architecture.md)                         | System design & data flow diagrams      |
  | [Data Dictionary](docs/data_dictionary.md)                         | Schema documentation for all tables     |
  | [Real Data Integration Guide](docs/Real_Data_Integration_Guide.md) | Replacing synthetic data with live APIs |

---

## 🤝 Contributing

Contributions are welcome! This project is part of a portfolio demonstrating end-to-end Revenue Operations engineering capabilities.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ☕ by <strong>Eduardo Cornelsen</strong> — © 2026 All Rights Reserved</sub><br/>
  <sub>Revenue Operations · Data Engineering · AI/ML · Full-Stack Development</sub>
</p>
