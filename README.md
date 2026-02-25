# 🚀 B2B Autonomous Lead Engine: RevOps Command Center

An advanced Revenue Operations (RevOps) dashboard and B2B lead generation pipeline simulation. Built with Streamlit, Plotly, and Pydantic, this repository demonstrates end-to-end RevOps competencies, from top-of-funnel lead discovery to predictive scenario modeling and post-sales retention.

## ✨ New Features in v3.0 (RevOps Edition)

We have transformed this application from a simple pipeline tracker into a **Portfolio-defining RevOps Platform**.

- **🔮 Revenue Scenario Modeler:** An interactive predictive engine. Adjust sliders for Lead Volume, Win Rate, ACV, and Cycle Time to simulate compounding mathematical effects on a 90-day time-series revenue trajectory.
- **🏦 Post-Sales & Expansion (NDR):** Track the "BowTie Funnel." Features Net Dollar Retention (NDR) metrics, Account Health scoring, and a dynamic ARR Composition Waterfall chart.
- **🧠 AI Explainability (XAI):** Executive-level Lead Intelligence scoring now includes direct textual explanations (e.g., "(+25 ICP) Strong revenue fit", "(-30 Needs penalty) Enterprise lock-in risk"). Hover over any lead score to see the AI reasoning.
- **💬 RevOps Copilot:** A GenAI iterative chat interface built to answer data-driven questions about pipeline risk, quota pacing, and sales rep performance directly inside the dashboard.
- **🎨 Cybermorphic UI/UX:** A sleek, modern dark-mode aesthetic featuring `@keyframes` staggered CSS load animations, neon gradients, and integrated metric tooltips.

---

## 🛠️ Tech Stack

| Layer             | Tools                                                              |
| ----------------- | ------------------------------------------------------------------ |
| **Frontend**      | Streamlit (`app.py`), Custom CSS, Plotly Graph Objects             |
| **Backend**       | Python 3.10+ · SQLite3 (`fct_scored_leads`, `dim_companies`)       |
| **Data Models**   | Pydantic v2 (`models.py`)                                          |
| **Data Simulation**| Faker, random weighted distributions (`sim_metrics.py`, `pipeline.py`) |
| **AI/ML**         | LLM prompt templates, Rule-based scoring, OpenAI/LangChain (Copilot) |
| **Testing**       | pytest                                                             |

## 🚀 Quickstart

1.  **Install Dependencies**
    ```bash
    conda create -n lead_engine python=3.10 -y
    conda activate lead_engine
    pip install streamlit pandas plotly pydantic faker pyyaml
    ```
2.  **Generate the Database Pipeline**
    This simulates SDR activity, enriches leads, and populates the SQLite database.
    ```bash
    python -m src.pipeline
    ```
3.  **Launch the Command Center**
    ```bash
    streamlit run src/dashboard/app.py
    ```

---

## 🏗️ System Architecture & Data Flow

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
│        │                                                         │           │
│        ▼                                                         ▼           │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     STAGE 5: CRM SYNC & HANDOFF                     │     │
│  │              HubSpot / Salesforce — Opportunity Management          │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Data Lineage & Pipeline

```text
ICP Config ──▶ Lead Discovery ──▶ Enrichment ──▶ Scoring ──▶ Outreach ──▶    CRM
  (YAML)      (Apollo/CNPJ)    (Hunter/BuiltWith)  (Rules/ML)   (Email)    (HubSpot)
                    │                   │               │           │           │
                    ▼                   ▼               ▼           ▼           ▼
               dim_companies    fct_enriched_leads  fct_scored  fct_outreach  Deals
               dim_contacts                         + deal_brief  _events    + Opps
```

---

## 📊 Dashboard Architecture

The Streamlit app is divided into distinct, purpose-built modules:

1.  **Revenue Dashboard:** The VP-level overview. Tracks Quota Attainment, Pipeline Coverage, Unit Economics (CAC/LTV), and real-time SDR pacing.
2.  **Generate Leads:** The execution engine. Filter the database by Firmographic and BANT signals, and "Queue" them into targeted outreach campaigns.
3.  **Lead Intelligence:** The tactical view. Search the active database with XAI tooltips explicitly explaining the `ScoringEngine` logic.
4.  **Sales Navigator:** Deep-dive into individual leads. Features AI-generated Deal Briefs, SPIN discovery questions, and BANT summaries.
5.  **Pipeline Analytics:** The conversion breakdown. Visualizes the funnel drop-off, Stage Velocity, Campaign ROI attribution, and the SDR Leaderboard.
6.  **Outreach Performance:** Tracks email cadence opens, replies, and "Response Types" grouped by week.
7.  **Post-Sales (NDR):** Expansion metrics tracking Gross vs Net Retention.
8.  **Scenario Modeler:** The "What-If" engine modeling cycle-time variances against quarterly targets.
9.  **RevOps Copilot:** The interactive AI chat agent predicting pipeline risk.

---

## 📁 Project Structure

```text
lead_engine/
├── README.md                    # This file (RevOps Edition)
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata
├── config/
│   └── icp_config.yaml          # Ideal Customer Profile definition
├── docs/
│   ├── architecture.md          # System architecture (Mermaid diagrams)
│   ├── data_dictionary.md       # Schema documentation
│   └── Real_Data_Integration_Guide.md # Guide to replacing synthetic APIs
├── src/
│   ├── pipeline.py              # End-to-end pipeline orchestrator
│   ├── config/
│   ├── models/
│   │   └── models.py            # Pydantic data models
│   ├── database/
│   │   ├── database.py          # SQLite database engine
│   │   └── seed_data.py         # Sample data generator
│   ├── discovery/               # Lead discovery engine (Stage 1)
│   ├── enrichment/              # Enrichment pipeline (Stage 2)
│   ├── scoring/                 # Scoring engine & XAI (Stage 3)
│   ├── api/                     # FastAPI application endpoints
│   ├── outreach/                # Outreach automation (Stage 4)
│   ├── crm/                     # CRM sync models (Stage 5)
│   └── dashboard/
│       ├── app.py               # Main Streamlit dashboard application
│       └── sim_metrics.py       # Simulation metric generators
└── tests/                       # Unit tests
```

---

## 🔌 Integrating Real Data

This project is currently powered by `src/pipeline.py` to generate realistic synthetic data for demonstration purposes without requiring expensive API keys.

To adapt this for a live production B2B SaaS environment, please refer to the specific integration instructions in:
👉 [`docs/Real_Data_Integration_Guide.md`](docs/Real_Data_Integration_Guide.md)
