# Data Dictionary — B2B Autonomous Lead Engine

## Overview

This document describes the schema for all data tables used in the B2B Lead Engine pipeline. In the MVP, all tables are stored in SQLite. In production, these map to BigQuery/Snowflake tables.

---

## `dim_companies` — Company Dimension Table

Stores unique company records discovered through ICP-based prospecting.

| Column           | Type     | Description                                    | Example                   |
| ---------------- | -------- | ---------------------------------------------- | ------------------------- |
| `company_id`     | TEXT PK  | Unique company identifier (UUID)               | `c-a1b2c3d4`              |
| `name`           | TEXT     | Company legal/trading name                     | `Acme Corp`               |
| `industry`       | TEXT     | Industry classification                        | `B2B SaaS`                |
| `country`        | TEXT     | Country code (ISO 3166)                        | `US`                      |
| `state`          | TEXT     | State/region code                              | `CA`                      |
| `employee_count` | INTEGER  | Estimated headcount                            | `150`                     |
| `revenue_usd`    | REAL     | Estimated annual revenue (USD)                 | `12000000.0`              |
| `website`        | TEXT     | Company website URL                            | `https://acme.com`        |
| `tech_stack`     | TEXT     | JSON array of detected technologies            | `["Sheets", "Mailchimp"]` |
| `funding_stage`  | TEXT     | Latest funding stage                           | `Series B`                |
| `founded_year`   | INTEGER  | Year founded                                   | `2019`                    |
| `cnpj`           | TEXT     | Brazilian CNPJ (null for non-BR)               | `12.345.678/0001-99`      |
| `cnae_code`      | TEXT     | Brazilian CNAE industry code (null for non-BR) | `6201-5`                  |
| `source`         | TEXT     | Discovery data source                          | `apollo`                  |
| `discovered_at`  | DATETIME | Timestamp of discovery                         | `2026-02-24T23:00:00Z`    |

---

## `dim_contacts` — Contact Dimension Table

Stores decision-maker contacts associated with companies.

| Column          | Type     | Description                      | Example                     |
| --------------- | -------- | -------------------------------- | --------------------------- |
| `contact_id`    | TEXT PK  | Unique contact identifier (UUID) | `ct-x1y2z3`                 |
| `company_id`    | TEXT FK  | Reference to `dim_companies`     | `c-a1b2c3d4`                |
| `full_name`     | TEXT     | Contact full name                | `Jane Smith`                |
| `title`         | TEXT     | Job title                        | `VP of Revenue Operations`  |
| `email`         | TEXT     | Business email                   | `jane@acme.com`             |
| `phone`         | TEXT     | Phone number                     | `+1-555-0123`               |
| `linkedin_url`  | TEXT     | LinkedIn profile URL             | `linkedin.com/in/janesmith` |
| `seniority`     | TEXT     | Seniority level                  | `VP`                        |
| `department`    | TEXT     | Department                       | `Revenue Operations`        |
| `source`        | TEXT     | Contact data source              | `hunter`                    |
| `verified`      | BOOLEAN  | Email verification status        | `true`                      |
| `discovered_at` | DATETIME | Timestamp of discovery           | `2026-02-24T23:00:00Z`      |

---

## `fct_enriched_leads` — Enriched Lead Fact Table

Unified lead records combining company + contact + enrichment signals.

| Column                    | Type     | Description                                 | Example                                  |
| ------------------------- | -------- | ------------------------------------------- | ---------------------------------------- |
| `lead_id`                 | TEXT PK  | Unique lead identifier (UUID)               | `l-m1n2o3`                               |
| `company_id`              | TEXT FK  | Reference to `dim_companies`                | `c-a1b2c3d4`                             |
| `contact_id`              | TEXT FK  | Reference to `dim_contacts`                 | `ct-x1y2z3`                              |
| `tech_stack_detected`     | TEXT     | JSON array of detected tech                 | `["Sheets", "Mailchimp"]`                |
| `tech_stack_gaps`         | TEXT     | JSON array of missing tech                  | `["CRM", "Analytics"]`                   |
| `buying_signals`          | TEXT     | JSON array of buying signals                | `["Recent funding", "Hiring SDRs"]`      |
| `social_signals`          | TEXT     | JSON summary of social engagement           | `{"posts_30d": 5, "engagement": "high"}` |
| `news_mentions`           | TEXT     | JSON array of recent news                   | `["Series B announced"]`                 |
| `enrichment_completeness` | REAL     | % of fields successfully enriched (0.0–1.0) | `0.85`                                   |
| `enrichment_sources`      | TEXT     | JSON array of sources used                  | `["apollo", "hunter", "builtwith"]`      |
| `enriched_at`             | DATETIME | Timestamp of enrichment                     | `2026-02-24T23:00:00Z`                   |

---

## `fct_scored_leads` — Scored Lead Fact Table

Leads with computed scores, BANT qualification, and AI-generated deal briefs.

| Column                 | Type     | Description                              | Example                |
| ---------------------- | -------- | ---------------------------------------- | ---------------------- |
| `lead_id`              | TEXT PK  | Reference to `fct_enriched_leads`        | `l-m1n2o3`             |
| `score`                | REAL     | Lead score (0–100)                       | `87.5`                 |
| `score_breakdown`      | TEXT     | JSON breakdown of score components       | `{"icp": 25, ...}`     |
| `qualification_status` | TEXT     | `qualified` / `nurture` / `disqualified` | `qualified`            |
| `budget_signal`        | BOOLEAN  | BANT: Budget indicator                   | `true`                 |
| `authority_signal`     | BOOLEAN  | BANT: Authority indicator                | `true`                 |
| `need_signal`          | BOOLEAN  | BANT: Need indicator                     | `true`                 |
| `timeline_signal`      | BOOLEAN  | BANT: Timeline indicator                 | `false`                |
| `deal_brief`           | TEXT     | AI-generated deal brief (full text)      | `"DEAL BRIEF: ..."`    |
| `deal_stage`           | TEXT     | Mapped CRM deal stage                    | `Qualified`            |
| `scored_at`            | DATETIME | Timestamp of scoring                     | `2026-02-24T23:00:00Z` |

---

## `fct_outreach_events` — Outreach Event Fact Table

Tracks all outreach interactions (emails, LinkedIn, responses).

| Column          | Type     | Description                                         | Example                   |
| --------------- | -------- | --------------------------------------------------- | ------------------------- |
| `event_id`      | TEXT PK  | Unique event identifier (UUID)                      | `e-p1q2r3`                |
| `lead_id`       | TEXT FK  | Reference to `fct_scored_leads`                     | `l-m1n2o3`                |
| `channel`       | TEXT     | `email` / `linkedin` / `phone`                      | `email`                   |
| `sequence_step` | INTEGER  | Step in outreach sequence (1, 2, 3)                 | `1`                       |
| `subject`       | TEXT     | Email subject line                                  | `Quick question about...` |
| `body`          | TEXT     | Email/message body                                  | `Hi Jane, I noticed...`   |
| `status`        | TEXT     | `sent` / `delivered` / `opened` / `replied`         | `sent`                    |
| `response_type` | TEXT     | `interested` / `not_now` / `not_interested` / `ooo` | `null`                    |
| `sent_at`       | DATETIME | Timestamp sent                                      | `2026-02-24T23:00:00Z`    |
| `opened_at`     | DATETIME | Timestamp opened (null if not tracked)              | `null`                    |
| `responded_at`  | DATETIME | Timestamp of response (null if no response)         | `null`                    |
