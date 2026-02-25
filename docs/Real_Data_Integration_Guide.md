# 🚀 The B2B Lead Engine: Real Data Integration Guide

This application is currently running purely on an internal SQLite simulation engine (`src/pipeline.py`) designed to demonstrate advanced RevOps analytics, XAI, and predictive scenario modeling without requiring external API keys.

To transition this dashboard from a portfolio simulation into a live production RevOps tool, follow these integration steps.

---

## Phase 1: CRM Integration (Salesforce / HubSpot)

The most critical step is replacing the `generate_revenue_metrics` and `generate_sfdc_opportunities` mock functions with live CRM data.

### 1. Salesforce (SFDC) via `simple-salesforce`
- **Action:** Install `simple-salesforce` (`pip install simple-salesforce`)
- **Integration:** Update `src/database/client.py` to authenticate via an SFDC Connected App.
- **Query:** Instead of simulating stages, query the `Opportunity` API object. 
```python
sf = Salesforce(username='myemail@example.com', password='password', security_token='token')
opps = sf.query("SELECT Id, Name, Amount, StageName, CloseDate, Probability FROM Opportunity WHERE IsClosed = False")
```
- **Mapping:** Map `StageName` to the Streamlit `render_crm()` and `render_pipeline_analytics()` waterfalls.

### 2. HubSpot via `hubspot-api-client`
- **Action:** If using HubSpot, use the official Python wrapper to fetch Deals.
- **Mapping:** Pull the `pipeline` and `dealstage` properties to populate the `pm["active_pipeline"]` variables in `app.py`.

---

## Phase 2: Lead Generation & Enrichment 

Currently, `src/discovery/search.py` and `src/enrichment/enricher.py` randomly generate fake companies. We need to point them to real data vendors.

### 1. Apollo.io API (Top of Funnel + Enrichment)
Apollo is the industry standard for B2B intelligence.
- **Action:** Replace `SimulatedSearch` with a real `requests.post()` to `https://api.apollo.io/v1/mixed_people/search`.
- **Mapping:** Map the Streamlit `render_generate_leads` Sidebar filters (Industry, Employees, Seniority) directly into the Apollo JSON payload.
- **Enrichment:** Use Apollo's `/v1/organizations/enrich` endpoint to populate the `tech_stack_gaps` and `funding_stage` used by the AI Scoring Engine.

### 2. Clearbit or ZoomInfo (Alternative Enrichment)
If you already have Clearbit, use their Reveal API to de-anonymize website traffic and push those domains into the `ScoreBreakdown` engine with a high "Intent/Behavioral" score.

---

## Phase 3: The AI RevOps Copilot (LangChain + OpenAI)

The `💬 RevOps Copilot` tab currently uses logic-branching based on keywords. To make it truly generative:

1. **Install LangChain:** `pip install langchain langchain-openai`
2. **Create a SQL Agent:** Connect LangChain directly to the `lead_engine.db` SQLite database using `create_sql_agent`.
3. **Execution:** When the user types "Which SDR has the best win rate?", LangChain will translate the natural language into a `SELECT` query against the `dim_contacts` and `fct_scored_leads` tables, execute it, and return a natural language summary to the Streamlit `st.chat_message`.

---

## Phase 4: Outreach Automation

Currently, clicking "📧 Queue Outreach" in the `⚡ Generate Leads` tab just downloads a CSV.

- **Action:** Integrate with Outreach.io, SalesLoft, or Lemlist via their REST APIs.
- **Workflow:** When the button is clicked, iterate over the `chosen` dataframe, and `POST` the contacts to a specific Sequence/Cadence ID.
- **Webhooks:** Set up a lightweight FastAPI script to catch webhooks from Outreach when an email is Opened or Replied, and use that to update `fct_outreach_events` in the SQLite database, powering the `📧 Outreach Performance` dashboard in real-time.
