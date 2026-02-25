"""
B2B Lead Engine — RevOps Command Center Dashboard v3

7 tabs: Revenue · Generate Leads · Lead Intelligence · Sales Navigator
        CRM / Salesforce · Pipeline Analytics · Outreach
All pages have date context + period filtering.
"""
from __future__ import annotations
import sys, csv, io
from pathlib import Path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from src.config.settings import settings
from src.database.database import Database
from src.dashboard.sim_metrics import (
    generate_daily_pipeline, generate_revenue_metrics,
    generate_campaign_data, generate_sdr_leaderboard,
    aggregate_weekly, generate_forecast, generate_stage_velocity,
    generate_risk_alerts, generate_sfdc_opportunities,
    filter_daily_by_dates, get_daily_date_range, compute_period_metrics,
    generate_daily_by_rep, SDR_NAMES,
)

st.set_page_config(page_title="LeadEngine RevOps", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(15px); }
  100% { opacity: 1; transform: translateY(0); }
}
.stApp{font-family:'Inter',-apple-system,sans-serif;background:linear-gradient(135deg,#020617 0%,#0f172a 50%,#1e3a8a 100%);animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;}
div[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(15,20,35,0.7),rgba(20,28,50,0.6));
backdrop-filter:blur(16px);border:1px solid rgba(148,163,184,0.1);border-top:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:20px 24px;
box-shadow:0 10px 30px -10px rgba(0,0,0,0.5);transition:all .3s cubic-bezier(0.4,0,0.2,1)}
div[data-testid="stMetric"]:hover{transform:translateY(-4px);border-color:rgba(233,69,96,0.5);box-shadow:0 20px 40px -15px rgba(233,69,96,0.2),inset 0 1px 0 rgba(255,255,255,0.1)}
div[data-testid="stMetric"] label{color:#94a3b8!important;font-size:.75rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:1px}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#f8fafc!important;font-weight:800!important;font-size:1.8rem!important;letter-spacing:-0.5px}
div[data-testid="stMetric"] [data-testid="stMetricDelta"]{font-weight:600!important;font-size:.85rem!important}
.metric-hero {border-image:linear-gradient(to right,#10b981,#3b82f6) 1;background:linear-gradient(145deg,rgba(16,185,129,0.05),rgba(59,130,246,0.05))}
.section-header{font-size:.75rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:2px;margin:24px 0 16px;padding-bottom:8px;border-bottom:1px solid rgba(148,163,184,0.15)}
.hero-banner{background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#312e81 100%);border:1px solid rgba(99,102,241,0.3);border-radius:20px;padding:32px 40px;margin-bottom:32px;position:relative;overflow:hidden;box-shadow:0 25px 50px -12px rgba(0,0,0,0.5)}
.hero-banner::before{content:'';position:absolute;top:-50%;right:-10%;width:400px;height:400px;background:radial-gradient(circle,rgba(99,102,241,0.2),transparent 70%);border-radius:50%}
.hero-banner h2{color:#f8fafc;font-weight:900;font-size:1.8rem;margin:0 0 8px;letter-spacing:-0.5px}.hero-banner p{color:#cbd5e1;margin:0;font-size:.95rem;font-weight:400}
.date-header{background:rgba(15,20,35,0.7);border:1px solid rgba(148,163,184,0.2);border-radius:12px;padding:12px 24px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;backdrop-filter:blur(8px)}
.date-header .period{color:#38bdf8;font-weight:700;font-size:.95rem}.date-header .range{color:#94a3b8;font-size:.85rem;font-weight:500}
.tag{display:inline-block;background:rgba(30,41,59,0.8);border:1px solid rgba(148,163,184,0.2);border-radius:6px;padding:4px 10px;margin:2px 4px 2px 0;font-size:.7rem;font-weight:600;color:#cbd5e1}
.signal-tag{display:inline-block;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:6px;padding:4px 10px;margin:2px 4px 2px 0;font-size:.7rem;font-weight:600;color:#34d399}
.bant-check{color:#10b981;font-weight:800}.bant-miss{color:#ef4444;opacity:.4}
.timeline-item{border-left:2px solid #334155;padding:12px 0 12px 20px;margin-left:12px;position:relative}
.timeline-item::before{content:'';position:absolute;left:-6px;top:16px;width:10px;height:10px;border-radius:50%;background:#334155}
.timeline-item.active{border-left-color:#38bdf8}.timeline-item.active::before{background:#38bdf8;box-shadow:0 0 8px rgba(56,189,248,0.5)}
.timeline-item.done{border-left-color:#10b981}.timeline-item.done::before{background:#10b981}
.alert-card{background:linear-gradient(90deg,rgba(30,41,59,0.6),rgba(15,23,42,0.8));border:1px solid rgba(148,163,184,0.1);border-radius:12px;padding:16px 20px;margin-bottom:12px;display:flex;align-items:flex-start;gap:16px;transition:all .2s}
.alert-card:hover{background:linear-gradient(90deg,rgba(30,41,59,0.8),rgba(15,23,42,0.9));transform:translateX(4px)}
.alert-card .icon{font-size:1.4rem;padding-top:2px}
.alert-card .content{flex:1}
.alert-card h4{margin:0 0 4px;font-size:.9rem;font-weight:700;color:#f8fafc}
.alert-card p{margin:0 0 8px;font-size:.8rem;color:#94a3b8}
.alert-card .action{font-size:.75rem;font-weight:600;display:inline-block;padding:4px 10px;border-radius:6px;background:rgba(255,255,255,0.05)}
.alert-high{border-left:4px solid #ef4444}.alert-high .action{color:#ef4444;background:rgba(239,68,68,0.1)}
.alert-medium{border-left:4px solid #f59e0b}.alert-medium .action{color:#f59e0b;background:rgba(245,158,11,0.1)}
.alert-low{border-left:4px solid #10b981}.alert-low .action{color:#10b981;background:rgba(16,185,129,0.1)}
.risk-badge{background:rgba(239,68,68,0.12);color:#ef4444;padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:700}
.stalled-badge{background:rgba(234,179,8,0.12);color:#eab308;padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:700}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0e17,#111827);border-right:1px solid rgba(233,69,96,0.1)}
section[data-testid="stSidebar"] .stSelectbox label,section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label,section[data-testid="stSidebar"] .stCheckbox label{
color:#64748b!important;font-size:.7rem!important;text-transform:uppercase;letter-spacing:.8px}
.stDataFrame{border-radius:12px;overflow:hidden}.stMarkdown a[href^="#"]{display:none!important}
.dash-footer{text-align:center;color:#475569;padding:16px;font-size:.78rem;border-top:1px solid rgba(233,69,96,0.1);margin-top:40px}
</style>
""", unsafe_allow_html=True)

# ── Cache ─────────────────────────────────────────────
@st.cache_resource
def get_database(): return Database(settings.database_path)

@st.cache_data(ttl=300)
def get_sim_data():
    daily = generate_daily_pipeline()
    sdr = generate_sdr_leaderboard()
    rep_daily = generate_daily_by_rep(daily)
    from src.dashboard.sim_metrics import generate_post_sales_metrics
    return {"daily": daily, "weekly": aggregate_weekly(daily), "rep_daily": rep_daily,
            "metrics": generate_revenue_metrics(daily),
            "campaigns": generate_campaign_data(), "sdr": sdr,
            "post_sales": generate_post_sales_metrics(),
            "forecast": generate_forecast(), "velocity": generate_stage_velocity(),
            "alerts": generate_risk_alerts(sdr), "sfdc": generate_sfdc_opportunities()}

# ── Helpers ───────────────────────────────────────────
FLAGS = {"US":"🇺🇸","BR":"🇧🇷","UK":"🇬🇧","DE":"🇩🇪","FR":"🇫🇷","IL":"🇮🇱","SG":"🇸🇬",
         "AU":"🇦🇺","CA":"🇨🇦","NL":"🇳🇱","SE":"🇸🇪","IN":"🇮🇳","JP":"🇯🇵","KR":"🇰🇷"}
PL = dict(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
          font=dict(color="#94a3b8",family="Inter",size=11),margin=dict(l=40,r=20,t=36,b=40),
          hoverlabel=dict(bgcolor="rgba(15,20,35,0.95)",font=dict(size=12,family="Inter",color="#f8fafc"),bordercolor="rgba(148,163,184,0.3)"))

def fmtr(v):
    if v>=1e9: return f"${v/1e9:.1f}B"
    if v>=1e6: return f"${v/1e6:.1f}M"
    if v>=1e3: return f"${v/1e3:,.0f}K"
    return f"${v:,.0f}"

def fmtn(v):
    if v>=1e6: return f"{v/1e6:.1f}M"
    if v>=1e3: return f"{v/1e3:.1f}K"
    return str(int(v))

def score_text(s):
    if s>=80: return f"🟢 {s:.0f}"
    if s>=60: return f"🟡 {s:.0f}"
    return f"🔴 {s:.0f}"

def dstr(pct, has_comp=True):
    if not has_comp: return None
    sign = "+" if pct>=0 else ""
    return f"{sign}{pct:.0f}%"

def date_banner(period, m):
    st.markdown(
        f'<div class="date-header">'
        f'<span class="period">📅 {period}</span>'
        f'<span class="range">{m["date_from"]} → {m["date_to"]} · {m["period_days"]} days'
        f'{" · vs previous period" if m["has_comparison"] else ""}</span>'
        f'</div>', unsafe_allow_html=True)

def _footer():
    st.markdown('<div class="dash-footer">LeadEngine v3.0 · <span style="color:#e94560;">B2B Autonomous Lead Engine</span> · RevOps Command Center</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    db = get_database()
    stats = db.get_pipeline_stats()
    if stats.get("dim_companies",0)==0:
        st.warning("⚠️ No data. Run: `python -m src.pipeline`"); return
    sim = get_sim_data()

    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:8px 0 16px;">'
            '<span style="font-size:2.2em;">🚀</span><br/>'
            '<span style="font-weight:800;font-size:1.15em;color:#f1f5f9;">LeadEngine</span><br/>'
            '<span style="font-size:.68rem;color:#e94560;text-transform:uppercase;letter-spacing:2px;font-weight:600;">RevOps Command Center</span>'
            '</div>', unsafe_allow_html=True)
        
        # CSS to highlight the first radio button ("AI RevOps Copilot")
        st.markdown("""
        <style>
        [data-testid="stRadio"] div[role="radiogroup"] > label:first-child {
            background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%);
            border-radius: 8px;
            padding: 8px 12px;
            color: #f8fafc !important;
            font-weight: 800;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.4);
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        [data-testid="stRadio"] div[role="radiogroup"] > label:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.6);
            border-color: rgba(99, 102, 241, 0.8);
        }
        [data-testid="stRadio"] div[role="radiogroup"] > label:first-child p {
            color: #f8fafc !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.divider()
        page = st.radio("Navigate", [
            "💬 AI RevOps Copilot",
            "📊 Revenue Dashboard","⚡ Generate Leads","🔍 Lead Intelligence",
            "🧭 Sales Navigator","💼 CRM / Salesforce","📈 Pipeline Analytics",
            "📧 Outreach","🏦 Post-Sales (NDR)","🔮 Scenario Modeler"],
            key="nav_radio",
            index=1,
            label_visibility="collapsed")

    # Pages that get date/rep filters
    ANALYTICS_PAGES = {"📊 Revenue Dashboard","💼 CRM / Salesforce","📈 Pipeline Analytics","📧 Outreach"}
    show_filters = page in ANALYTICS_PAGES

    # ── Top Filter Bar (only on analytics pages) ──────
    min_d, max_d = get_daily_date_range(sim["daily"])
    from datetime import timedelta

    # Initialize defaults in session state
    if "preset" not in st.session_state:
        st.session_state["preset"] = "Last 30 Days"
        st.session_state["sd"] = max_d - timedelta(days=29)
        st.session_state["ed"] = max_d
        st.session_state["rep"] = "🏢 Whole Team"

    if show_filters:
        def on_preset_change():
            p = st.session_state["preset"]
            if p == "Last 30 Days":
                st.session_state["sd"] = max_d - timedelta(days=29)
                st.session_state["ed"] = max_d
            elif p == "Last 60 Days":
                st.session_state["sd"] = max_d - timedelta(days=59)
                st.session_state["ed"] = max_d
            elif p == "Full Quarter":
                st.session_state["sd"] = min_d
                st.session_state["ed"] = max_d

        def reset_date_filters():
            st.session_state["preset"] = "Last 30 Days"
            st.session_state["sd"] = max_d - timedelta(days=29)
            st.session_state["ed"] = max_d
            st.session_state["rep"] = "🏢 Whole Team"

        tf1, tf2, tf3, tf_reset, tf4 = st.columns([1.1, 1.1, 1.3, 0.8, 1.5])
        with tf1:
            start_date = st.date_input("📅 From", min_value=min_d, max_value=max_d, key="sd")
        with tf2:
            end_date = st.date_input("📅 To", min_value=min_d, max_value=max_d, key="ed")
        with tf3:
            preset = st.selectbox("Period", ["Custom","Last 30 Days","Last 60 Days","Full Quarter"],
                                  key="preset", on_change=on_preset_change)
        with tf_reset:
            st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
            st.button("🔄 Reset", on_click=reset_date_filters, use_container_width=True)
        with tf4:
            rep_options = ["🏢 Whole Team"] + [f"👤 {n}" for n in SDR_NAMES]
            selected_rep = st.selectbox("👤 Sales Rep", rep_options, key="rep")
    else:
        start_date = st.session_state.get("sd", max_d - timedelta(days=29))
        end_date = st.session_state.get("ed", max_d)
        selected_rep = st.session_state.get("rep", "🏢 Whole Team")

    # Compute period metrics — apply date range and optional rep filter
    is_whole_team = selected_rep.startswith("🏢")
    rep_name = selected_rep.replace("👤 ","") if not is_whole_team else None
    source_daily = sim["daily"] if is_whole_team else sim["rep_daily"].get(rep_name, sim["daily"])
    current, previous = filter_daily_by_dates(source_daily, start_date, end_date)
    period_label = f"{start_date} → {end_date}"
    if not is_whole_team:
        period_label += f" · {rep_name}"
    pm = compute_period_metrics(current, previous, is_individual_rep=not is_whole_team)

    if   page=="📊 Revenue Dashboard":   render_revenue(db,stats,sim,pm,period_label,current,rep_name)
    elif page=="⚡ Generate Leads":      render_generate_leads(db,stats)
    elif page=="🔍 Lead Intelligence":   render_lead_intelligence(db,stats)
    elif page=="🧭 Sales Navigator":     render_sales_navigator(db,stats)
    elif page=="💼 CRM / Salesforce":    render_crm(sim,pm,period_label,start_date,end_date,rep_name)
    elif page=="📈 Pipeline Analytics":  render_pipeline_analytics(db,stats,sim,pm,period_label,current,rep_name)
    elif page=="📧 Outreach":            render_outreach(db,stats,sim,pm,period_label,current)
    elif page=="🏦 Post-Sales (NDR)":    render_post_sales(sim["post_sales"])
    elif page=="🔮 Scenario Modeler":    render_scenario_modeler(pm, rep_name)
    elif page=="💬 AI RevOps Copilot":   render_copilot(pm, stats)


# ══════════════════════════════════════════════════════
# 10. REVOPS COPILOT (GenAI Chat)
# ══════════════════════════════════════════════════════
def render_copilot(pm, stats):
    st.markdown("## 💬 AI RevOps Copilot")
    st.caption("Ask questions about your pipeline, targets, or opportunities in natural language.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to your command center. I am analyzing your real-time data. What would you like to know about our revenue trajectory?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Quick action buttons
    c1, c2, c3 = st.columns(3)
    quick_prompt = None
    with c1:
        if st.button("📊 Analyze Pipeline Risk", use_container_width=True): quick_prompt = "Analyze Pipeline Risk"
        if st.button("👑 CEO: Company Valuation Status", use_container_width=True): quick_prompt = "CEO: Company Valuation Status"
    with c2:
        if st.button("🎯 Sales Forecast to Target", use_container_width=True): quick_prompt = "Forecast vs Target"
        if st.button("📈 VP Sales: Rep Performance", use_container_width=True): quick_prompt = "VP Sales: Rep Performance Breakdown"
    with c3:
        if st.button("💡 Provide Executive Summary", use_container_width=True): quick_prompt = "Executive Summary"
        if st.button("🏦 VP Revenue: Net Retention Forecast", use_container_width=True): quick_prompt = "VP Revenue: Net Retention Forecast"

    # Chat logic
    prompt = st.chat_input("Ask about revenue, conversions, or specific reps...")
    if quick_prompt: prompt = quick_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing RevOps engine..."):
                import time
                time.sleep(1.2) # Simulate LLM API delay
                
                # Mocked intelligent responses utilizing actual DB context
                if "risk" in prompt.lower():
                    resp = f"**Pipeline Risk Analysis:** Coverage is currently at {pm['coverage_ratio']:.1f}x (Target is 3.0x). We have {stats['funnel_pipeline']} leads active, but {pm['total_deals']} won so far. Your highest risk is in the **Negotiation** stage where cycle times have increased by 14% this quarter. I recommend launching targeted C-Level outreach to accelerate these {stats.get('outreach_sent', 0)} active touches."
                elif "forecast" in prompt.lower() or "target" in prompt.lower():
                    resp = f"**Forecast Trajectory:** You are trending at {pm['quota_attainment']:.1f}% of quota. Based on a current Active Pipeline of {fmtr(pm['active_pipeline'])} and a win rate of {pm['win_rate']:.1f}%, you must increase top-of-funnel Lead Generation by approximately 22% over the next 3 weeks to hit the baseline target of {fmtr(pm['revenue_target'])}."
                elif "summary" in prompt.lower() or "executive" in prompt.lower():
                    resp = f"**Executive Status (C-Level Brief):**\n\n* **Topline:** {fmtr(pm['total_revenue'])} Booked.\n* **Efficiency:** Customer Acquisition Cost (CAC) is holding steady at {fmtr(pm.get('cac', 0))}. The LTV/CAC ratio is {pm.get('ltv_cac_ratio', 0.0):.1f}x.\n* **Velocity:** The sales engine is cycling deals in {pm['avg_cycle_days']} days.\n* **Action Item:** Instruct SDRs to leverage the newly rolled out XAI intelligence tags to prioritize the 16 highly-qualified new logos in the pipeline."
                else:
                    resp = f"I've registered your query regarding '{prompt}'. In a fully integrated LangChain/OpenAI environment, I would execute a SQL query against the `fct_scored_leads` and `dim_companies` tables, formulate a pandas dataframe visualization, and provide deep analytical reasoning spanning all {stats['funnel_qualified_companies']} unique companies in your active funnel."

                st.markdown(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})


# ══════════════════════════════════════════════════════
# 9. POST-SALES & RETENTION (Advanced RevOps)
# ══════════════════════════════════════════════════════
def render_post_sales(psm):
    st.markdown("## 🏦 Post-Sales & Expansion")
    st.caption("Tracking Net Dollar Retention, Account Health, and Upsell Pipeline across the active customer base.")

    # Retention BANs
    st.markdown('<div class="section-header">🛡️ RETENTION METRICS</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Net Dollar Retention", f"{psm['ndr']:.1f}%", help="Starting ARR + Expansion - Contraction - Churn / Starting ARR. Benchmark >110%.")
    with r2:
        st.metric("Gross Revenue Retention", f"{psm['grr']:.1f}%", help="Starting ARR - Contraction - Churn / Starting ARR. Benchmark >90%.")
    with r3:
        st.metric("Active Renewals (90d)", fmtr(psm['active_renewals_90d']))
    with r4:
        st.metric("Logo Churn Rate", f"{psm['logo_churn_rate']:.1f}%", delta="0.5% vs target", delta_color="inverse")

    st.divider()
    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.markdown("### 📈 ARR Composition Waterfall")
        # Ensure positive values for the raw numbers so plotly calculates correctly
        starting_arr = psm["starting_arr"]
        new_logos = 1850000
        expansion = psm["expansion_arr"]
        contraction = -250000
        churn = -400000
        ending_arr = psm["ending_arr"]

        fig = go.Figure(go.Waterfall(
            name="ARR", orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Starting ARR", "New Logos", "Expansion", "Contraction", "Churn", "Ending ARR"],
            textposition="outside",
            text=[fmtr(abs(v)) for v in [starting_arr, new_logos, expansion, contraction, churn, ending_arr]],
            y=[starting_arr, new_logos, expansion, contraction, churn, 0],
            connector={"line":{"color":"rgba(148,163,184,0.15)","width":1,"dash":"dot"}},
            decreasing={"marker":{"color":"#ef4444"}},
            increasing={"marker":{"color":"#10b981"}},
            totals={"marker":{"color":"#6366f1"}}
        ))
        fig.update_layout(**PL, height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### ❤️ Account Health Scores")
        h = psm["health_tiers"]
        h_labels = ["Healthy (🟢)", "At Risk (🟡)", "Critical Risk (🔴)"]
        h_vals = [h["healthy"]["count"], h["at_risk"]["count"], h["critical"]["count"]]
        h_colors = [h["healthy"]["color"], h["at_risk"]["color"], h["critical"]["color"]]

        fig = go.Figure(data=[go.Pie(
            labels=h_labels, values=h_vals, hole=.6,
            marker=dict(colors=h_colors, line=dict(color='rgba(15,23,42,1)', width=2)),
            textinfo="label+value"
        )])
        
        # Merge the global PL dict but override the margin for this specific pie chart
        pie_layout = PL.copy()
        pie_layout["margin"] = dict(t=20, b=20, l=20, r=20)
        fig.update_layout(**pie_layout, height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk ARR Summary inline
        st.markdown(f"""
        <div style='background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);padding:16px;border-radius:12px;margin-top:-20px;'>
            <div style='color:#ef4444;font-size:0.8rem;text-transform:uppercase;font-weight:700;'>Revenue at Critical Risk</div>
            <div style='color:#f8fafc;font-size:1.8rem;font-weight:900;'>{fmtr(h["critical"]["arr"])}</div>
        </div>
        """, unsafe_allow_html=True)
def render_scenario_modeler(pm, rep_name=None):
    title_suffix = f" — {rep_name}" if rep_name else ""
    st.markdown(f"## 🔮 Revenue Scenario Modeler{title_suffix}")
    st.caption("Adjust key levers below to instantly project end-of-quarter pipeline and revenue outcomes.")

    # Current baseline metrics
    base_leads = pm["total_leads"] if pm["total_leads"] > 0 else 100
    base_win_rate = pm["win_rate"] if pm["win_rate"] > 0 else 15.0
    base_acv = pm["avg_deal_size"] if pm["avg_deal_size"] > 0 else 45000
    base_cycle = pm["avg_cycle_days"] if pm["avg_cycle_days"] > 0 else 45

    st.markdown('<div class="section-header">🎛️ REVENUE LEVERS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        mod_leads = st.slider("Lead Volume Δ (%)", -50, 150, 0, 5, help="Increase/decrease total top-of-funnel leads.")
    with c2:
        mod_win_rate = st.slider("Win Rate Δ (Abs %)", -10.0, 20.0, 0.0, 0.5, help="Absolute % increase to Win Rate.")
    with c3:
        mod_acv = st.slider("ACV Δ (%)", -30, 100, 0, 5, help="Increase/decrease Average Contract Value.")
    with c4:
        mod_cycle = st.slider("Cycle Time Δ (Days)", -30, 30, 0, 1, help="Accelerate (-) or decelerate (+) sales velocity.")

    st.divider()

    # Calculations
    proj_leads = int(base_leads * (1 + mod_leads / 100.0))
    # Keep conversion rates stable to isolate the sliders
    proj_deals = int(proj_leads * (pm["conversion_rate"]/100.0) * ((base_win_rate + mod_win_rate)/100.0))
    proj_acv = base_acv * (1 + mod_acv / 100.0)
    proj_rev = proj_deals * proj_acv
    proj_cycle = max(1, base_cycle + mod_cycle)
    
    base_rev = pm["total_revenue"]
    rev_diff = proj_rev - base_rev

    st.markdown('<div class="section-header">📈 PROJECTED OUTCOMES</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Projected Revenue", fmtr(proj_rev), delta=f"{fmtr(rev_diff)} vs baseline")
    with r2:
        st.metric("Projected Deals Won", fmtn(proj_deals), delta=f"{int(proj_deals - pm['total_deals'])} deals")
    with r3:
        st.metric("Projected ACV", fmtr(proj_acv), delta=f"{mod_acv}%" if mod_acv else None)
    with r4:
        st.metric("Projected Velocity", f"{proj_cycle} days", delta=f"{mod_cycle} days", delta_color="inverse")

    # Modeler Chart - Time Series Projection
    st.divider()

    # Dynamic Insights Engine
    st.markdown('<div class="section-header">🤖 AI SCENARIO INSIGHTS</div>', unsafe_allow_html=True)
    if proj_rev >= pm["revenue_target"]:
        st.success(f"**Target Attainable:** This scenario generates **{fmtr(proj_rev - pm['revenue_target'])} above quota**. {'The accelerated sales velocity is pulling revenue forward.' if mod_cycle < 0 else 'Even with cycle delays, sheer volume covers the spread.'}")
    elif proj_rev > pm["total_revenue"]:
        rev_diff = proj_rev - pm["total_revenue"]
        st.warning(f"**Growth, but missing quota:** Revenue grows {fmtr(rev_diff)}, but you still miss the {fmtr(pm['revenue_target'])} target by {fmtr(pm['revenue_target'] - proj_rev)}. Recommend increasing pipeline volume.")
    else:
        rev_diff = proj_rev - pm["total_revenue"]
        st.error(f"**Severe Revenue Contraction:** This scenario results in a {fmtr(abs(rev_diff))} loss against baseline pace. {'Cycle time delays are pushing closed-won dates out of the quarter.' if mod_cycle > 10 else 'Falling win rates are bleeding pipeline value.'}")

    # Modeler Chart - Time Series Projection
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Generate 90-day forward-looking trajectory
    days = np.arange(1, 91)
    
    # Baseline curve (smooth S-curve adoption)
    base_target = pm["revenue_target"]
    base_curve = base_rev + (base_target - base_rev) * (1 / (1 + np.exp(-0.08 * (days - base_cycle))))
    
    # Projected curve (delayed/accelerated by proj_cycle, peaking at proj_rev)
    proj_curve = base_rev + (proj_rev - base_rev) * (1 / (1 + np.exp(-0.08 * (days - proj_cycle))))
    
    # Flat target line
    target_line = np.full(90, base_target)

    fig = go.Figure()
    
    # Quota Target
    fig.add_trace(go.Scatter(x=days, y=target_line, mode="lines", name="Target Quota", 
                             line=dict(color="#64748b", width=2, dash="dash")))
    
    # Baseline Trajectory
    fig.add_trace(go.Scatter(x=days, y=base_curve, mode="lines", name=f"Baseline Pace ({base_cycle}d cycle)",
                             line=dict(color="rgba(99,102,241,0.6)", width=3),
                             fill="tozeroy", fillcolor="rgba(99,102,241,0.05)"))
                             
    # Projected Trajectory
    proj_color = "#10b981" if proj_rev >= base_target else "#ef4444"
    fig.add_trace(go.Scatter(x=days, y=proj_curve, mode="lines", name=f"Projected Pace ({proj_cycle}d cycle)",
                             line=dict(color=proj_color, width=4)))

    fig.update_layout(**PL, height=450, 
                      yaxis_title="Cumulative Pipeline Revenue ($)",
                      xaxis_title="Days Forward (Next 90 Days)",
                      legend=dict(orientation="h", y=1.12, x=0.0))
    st.plotly_chart(fig, use_container_width=True)




# ══════════════════════════════════════════════════════
# 1. REVENUE DASHBOARD
# ══════════════════════════════════════════════════════
def render_revenue(db,stats,sim,pm,period,current,rep_name=None):
    from src.dashboard.sim_metrics import generate_forecast
    fc = generate_forecast(pm["active_pipeline"])
    st.markdown("## Revenue Dashboard")
    date_banner(period, pm)

    # Group 1: Executive Health Metrics
    st.markdown('<div class="section-header">📈 Executive Health</div>', unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("💰 REVENUE", fmtr(pm["total_revenue"]), dstr(pm["rev_delta"],pm["has_comparison"]))
    with k2: st.metric("📊 PIPELINE", fmtr(pm["active_pipeline"]), dstr(pm.get("pipe_delta",0),pm["has_comparison"]))
    with k3: st.metric("🎯 QUOTA", f'{pm["quota_attainment"]:.0f}%', f'Target: {fmtr(pm["revenue_target"])}')
    with k4: st.metric("📈 COVERAGE", f'{pm["coverage_ratio"]:.1f}x', "🟢 OK" if pm["coverage_ratio"]>=3 else "🔴 Low")

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # Group 2: Sales Engine Tactical Metrics
    st.markdown('<div class="section-header">⚡ Sales Engine</div>', unsafe_allow_html=True)
    k7,k8,k9,k10,k11,k12 = st.columns(6)
    with k7:  st.metric("📥 LEADS", fmtn(pm["total_leads"]), dstr(pm["leads_delta"],pm["has_comparison"]))
    with k8:  st.metric("✅ QUALIFIED", fmtn(pm["total_qualified"]), dstr(pm["qual_delta"],pm["has_comparison"]))
    with k9:  st.metric("📅 MEETINGS", fmtn(pm["total_meetings"]), dstr(pm["meetings_delta"],pm["has_comparison"]))
    with k10: st.metric("🤝 DEALS WON", fmtn(pm["total_deals"]), dstr(pm["deals_delta"],pm["has_comparison"]))
    with k11: st.metric("🏆 WIN RATE", f'{pm["win_rate"]:.1f}%', dstr(pm.get("win_delta",0),pm["has_comparison"]))
    with k12: st.metric("⏱️ CYCLE", f'{pm["avg_cycle_days"]}d', dstr(pm.get("cycle_delta",0),pm["has_comparison"]))

    st.divider()

    # Unit Economics + Quota Gauge + Alerts
    g1,g2,g3 = st.columns(3)

    with g1:
        label = f"🎯 Quota — {rep_name}" if rep_name else "🎯 Quota Attainment"
        st.markdown(f"### {label}")
        att = pm["quota_attainment"]
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=att,
            number={"suffix":"%","font":{"size":44,"color":"#f1f5f9","family":"Inter"}},
            delta={"reference":100,"valueformat":".0f","suffix":"%"},
            gauge={"axis":{"range":[0,150],"tickcolor":"#475569"},
                   "bar":{"color":"#10b981" if att>=100 else "#f59e0b" if att>=70 else "#ef4444"},
                   "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                   "steps":[{"range":[0,70],"color":"rgba(239,68,68,0.08)"},
                            {"range":[70,100],"color":"rgba(245,158,11,0.08)"},
                            {"range":[100,150],"color":"rgba(16,185,129,0.08)"}],
                   "threshold":{"line":{"color":"#f1f5f9","width":2},"thickness":.8,"value":100}}))
        fig.update_layout(**PL, height=240)
        st.plotly_chart(fig, use_container_width=True)
        # $ amount below the gauge
        rev_c = "#22c55e" if att >= 100 else "#eab308" if att >= 70 else "#ef4444"
        st.markdown(
            f'<div style="text-align:center;margin-top:-10px;">'
            f'<span style="font-size:1.4em;font-weight:800;color:{rev_c};">{fmtr(pm["quota_revenue"])}</span>'
            f' <span style="color:#64748b;font-size:.85em;">of {fmtr(pm["quota_target_amount"])} target</span>'
            f'</div>', unsafe_allow_html=True)

    with g2:
        econ_label = f"💲 Unit Economics — {rep_name}" if rep_name else "💲 Unit Economics"
        st.markdown(f"### {econ_label}")
        st.markdown("")
        ue1,ue2 = st.columns(2)
        with ue1:
            st.metric("Customer Acquisition Cost", fmtr(pm["cac"]) if pm["total_deals"] > 0 else "N/A", help="Total Marketing & SDR Spend ÷ Total Deals Won")
            st.metric("Lifetime Value", fmtr(pm["ltv"]) if pm["total_deals"] > 0 else "N/A", help="Est. 2.8x Expansion Multiplier over 3 years")
        with ue2:
            st.metric("LTV : CAC Ratio", f'{pm["ltv_cac_ratio"]:.1f}x', help="Target B2B SaaS benchmark is > 3.0x")
            st.metric("Total Ad Spend", fmtr(pm["total_spend"]))

    with g3:
        alert_label = f"🚨 Alerts — {rep_name}" if rep_name else "🚨 Risk Alerts"
        st.markdown(f"### {alert_label}")
        # Dynamic alerts based on actual pm data
        dyn_alerts = []
        if pm["quota_attainment"] < 70:
            dyn_alerts.append({"severity":"high","icon":"🔴","type":"Below Quota",
                "message":f'At {pm["quota_attainment"]:.0f}% — {fmtr(pm["quota_target_amount"] - pm["quota_revenue"])} gap to target',
                "action":"Accelerate pipeline, review stalled deals"})
        elif pm["quota_attainment"] < 100:
            dyn_alerts.append({"severity":"medium","icon":"🟡","type":"Quota at Risk",
                "message":f'At {pm["quota_attainment"]:.0f}% — {fmtr(pm["quota_target_amount"] - pm["quota_revenue"])} remaining',
                "action":"Focus on late-stage deals, push for close"})
        else:
            dyn_alerts.append({"severity":"low","icon":"🟢","type":"Quota Exceeded",
                "message":f'At {pm["quota_attainment"]:.0f}% — {fmtr(pm["quota_revenue"] - pm["quota_target_amount"])} over target',
                "action":"Maintain momentum, build pipeline for next quarter"})
        if pm["coverage_ratio"] < 3:
            dyn_alerts.append({"severity":"high","icon":"🔴","type":"Low Coverage",
                "message":f'Coverage ratio at {pm["coverage_ratio"]:.1f}x — below 3x minimum',
                "action":"Increase outbound volume or add new pipeline source"})
        if pm["win_rate"] < 15:
            dyn_alerts.append({"severity":"medium","icon":"🟡","type":"Low Win Rate",
                "message":f'Win rate at {pm["win_rate"]:.1f}% — below 15% threshold',
                "action":"Review qualification criteria, improve discovery"})
        if pm["conversion_rate"] > 30:
            dyn_alerts.append({"severity":"low","icon":"🟢","type":"Strong Conversion",
                "message":f'Lead→Qualified at {pm["conversion_rate"]:.1f}% — above 30% benchmark',
                "action":"Scale campaign spend to capitalize on momentum"})
        if pm["ltv_cac_ratio"] > 3:
            dyn_alerts.append({"severity":"low","icon":"🟢","type":"Healthy Unit Economics",
                "message":f'LTV:CAC at {pm["ltv_cac_ratio"]:.1f}x — above 3x benchmark',
                "action":"Room to increase acquisition spend"})
        for a in dyn_alerts[:3]:  # Top 3
            severity_class = f"alert-{a['severity']}"
            html = f"""
            <div class="alert-card {severity_class}">
                <div class="icon">{a['icon']}</div>
                <div class="content">
                    <h4>{a['type']}</h4>
                    <p>{a['message']}</p>
                    <div class="action">{a['action']}</div>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

    st.divider()

    # Revenue Trend + Funnel
    c1,c2 = st.columns([3,2])
    with c1:
        title_suffix = f" — {rep_name}" if rep_name else ""
        st.markdown(f"### 📈 Revenue & Pipeline Trend{title_suffix}")
        
        # Trend Controls
        tc1, tc2, tc3 = st.columns([1, 1, 2])
        with tc1:
            agg_level = st.selectbox("View by", ["Day", "Week", "Month", "Quarter"], index=1, label_visibility="collapsed")
        with tc2:
            is_cumulative = st.checkbox("Cumulative", value=False)
        with tc3:
            show_pipeline = st.checkbox("Show Pipeline", value=True)

        # Aggregate data dynamically
        import pandas as pd
        if current:
            df_cur = pd.DataFrame(current)
            df_cur["date_obj"] = pd.to_datetime(df_cur["date_obj"])
            
            freq_map = {"Day": "D", "Week": "W-MON", "Month": "ME", "Quarter": "QE"}
            freq = freq_map[agg_level]
            
            df_agg = df_cur.groupby(pd.Grouper(key="date_obj", freq=freq)).agg({
                "revenue": "sum", "pipeline_value": "last"
            }).reset_index()
            # Drop empty periods
            df_agg = df_agg.dropna(subset=["revenue"])
            
            df_agg["date_str"] = df_agg["date_obj"].dt.strftime("%b %d, %Y")
            
            if is_cumulative:
                df_agg["revenue"] = df_agg["revenue"].cumsum()
                
            y_rev = df_agg["revenue"].tolist()
            y_pipe = df_agg["pipeline_value"].tolist()
            x_dates = df_agg["date_str"].tolist()
            n_periods = len(df_agg)
        else:
            y_rev, y_pipe, x_dates, n_periods = [], [], [], 1

        fig = go.Figure()
        
        # Revenue trace
        fill = "tozeroy" if not is_cumulative else "none"
        fig.add_trace(go.Scatter(x=x_dates,y=y_rev,
            mode="lines+markers",name="Cumulative Revenue" if is_cumulative else "Revenue",
            line=dict(color="#10b981",width=3),marker=dict(size=6,color="#34d399"),
            fill=fill,fillcolor="rgba(16,185,129,0.1)"))

        # Pipeline trace
        if show_pipeline:
            fig.add_trace(go.Scatter(x=x_dates,y=y_pipe,
                mode="lines",name="Pipeline (End of Period)",line=dict(color="#6366f1",width=2,dash="dot")))

        # Target line
        if n_periods > 0:
            if agg_level == "Day": target_per_period = pm["revenue_target"] / 90
            elif agg_level == "Week": target_per_period = pm["revenue_target"] / 13
            elif agg_level == "Month": target_per_period = pm["revenue_target"] / 3
            else: target_per_period = pm["revenue_target"]
            
            if is_cumulative:
                target_vals = [target_per_period * (i+1) for i in range(n_periods)]
                tgt_name = "Cumulative Target"
            else:
                target_vals = [target_per_period] * n_periods
                tgt_name = f"Target ({fmtr(target_per_period)}/{agg_level[:1]})"
                
            fig.add_trace(go.Scatter(
                x=x_dates, y=target_vals,
                mode="lines", name=tgt_name,
                line=dict(color="#ef4444", width=2, dash="dash")))

        fig.update_layout(**PL,height=380,showlegend=True,legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"### Lead Funnel & Conversion{title_suffix}")
        # Dynamic funnel from period-filtered metrics
        fv = [pm["total_leads"], pm["total_qualified"], pm["total_meetings"], pm["total_deals"]]
        # Modern gradient mapped to funnel stages
        c = ["#3b82f6","#6366f1","#8b5cf6","#ec4899"]
        fig = go.Figure(go.Funnel(y=["Leads Generated","Qualified","Meetings","Deals Won"],
            x=fv, textinfo="value+percent initial",
            marker=dict(color=c,line=dict(width=1,color="rgba(255,255,255,0.1)")),
            connector=dict(line=dict(color="rgba(148,163,184,0.15)",width=1,dash="dot"))))
        fig.update_layout(**PL,height=380,showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Forecast — dynamic per rep
    st.markdown(f"### 📊 Revenue Forecast{title_suffix}")
    fstages = fc["stages"]
    # Scale forecast by rep's proportion of total revenue
    if rep_name:
        # Compute rep share from revenue (team total from sim metrics)
        team_rev = sim["metrics"]["total_revenue"]
        rep_share = pm["total_revenue"] / team_rev if team_rev else 0.125
        scaled_stages = [{"stage":s["stage"],"value":round(s["value"]*rep_share,-2),
                          "probability":s["probability"],"deals":max(1,int(s["deals"]*rep_share))} for s in fstages]
    else:
        scaled_stages = fstages
        rep_share = 1.0

    f1,f2,f3 = st.columns([4,1,1])
    with f1:
        fig = go.Figure()
        fig.add_trace(go.Bar(y=[s["stage"] for s in scaled_stages],x=[s["value"] for s in scaled_stages],
            orientation="h",name="Unweighted",marker_color="rgba(56,189,248,0.2)",
            text=[fmtr(s["value"]) for s in scaled_stages],textposition="auto"))
        fig.add_trace(go.Bar(y=[s["stage"] for s in scaled_stages],
            x=[s["value"]*s["probability"] for s in scaled_stages],orientation="h",name="Weighted",
            marker_color="#38bdf8",text=[f'{fmtr(s["value"]*s["probability"])} ({s["probability"]*100:.0f}%)' for s in scaled_stages],
            textposition="auto"))
        fig.update_layout(**PL,height=300,barmode="overlay",legend=dict(orientation="h",y=1.12),
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    with f2:
        best = sum(s["value"] for s in scaled_stages if s["probability"]>=0.25)
        weighted = sum(s["value"]*s["probability"] for s in scaled_stages)
        st.metric("Best Case",fmtr(best)); st.metric("Weighted",fmtr(weighted))
    with f3:
        total_pipe = sum(s["value"] for s in scaled_stages)
        total_deals = sum(s["deals"] for s in scaled_stages)
        st.metric("Total Pipeline",fmtr(total_pipe)); st.metric("Deals in Pipe",total_deals)
    _footer()


# ══════════════════════════════════════════════════════
# 2. GENERATE LEADS (independent tab)
# ══════════════════════════════════════════════════════
def render_generate_leads(db,stats):
    st.markdown("## ⚡ Generate Leads")
    st.caption("Apply filters, discover qualified leads, import into campaigns")
    st.markdown(
        '<div class="hero-banner"><h2>⚡ Lead Generation Engine</h2>'
        '<p>Set your ICP criteria below and instantly discover, qualify, and import leads</p></div>',
        unsafe_allow_html=True)

    fc1,fc2,fc3,fc4 = st.columns(4)
    with fc1:
        mkts = db.get_unique_values("country","dim_companies")
        gm = st.multiselect("Market",[f"{FLAGS.get(m,'🌐')} {m}" for m in mkts],key="gm")
        mc = [m.split(" ")[-1] for m in gm] if gm else None
    with fc2: gi = st.multiselect("Industry",db.get_unique_values("industry","dim_companies"),key="gi") or None
    with fc3:
        gs = st.slider("Min Score",0,100,0,key="gs")
        gs_v = gs if gs>0 else None
    with fc4: gst = st.multiselect("Status",["qualified","nurture","disqualified"],default=["qualified","nurture"],key="gst") or None

    with st.sidebar:
        st.divider()
        st.markdown("### 🎛️ Advanced Filters")
        rev_min = st.number_input("Min Revenue ($)",0,value=0,step=1000000,key="gl_rmin")
        rev_max = st.number_input("Max Revenue ($)",0,value=0,step=1000000,key="gl_rmax")
        emp = st.slider("Employees",0,5000,(0,5000),key="gl_emp")
        fsen = st.multiselect("Seniority",db.get_unique_values("seniority","dim_contacts"),key="gl_sen") or None
        fsrc = st.multiselect("Source",db.get_unique_values("source","dim_companies"),key="gl_src") or None
        bb=st.checkbox("Budget ✅",key="gl_b"); ba=st.checkbox("Authority ✅",key="gl_a")
        bn=st.checkbox("Need ✅",key="gl_n"); bt=st.checkbox("Timeline ✅",key="gl_t")

    results = db.search_leads(markets=mc,industries=gi,score_min=gs_v,statuses=gst,
        revenue_min=rev_min if rev_min>0 else None,revenue_max=rev_max if rev_max>0 else None,
        employees_min=emp[0] if emp[0]>0 else None,employees_max=emp[1] if emp[1]<5000 else None,
        seniorities=fsen,sources=fsrc,
        bant_budget=True if bb else None,bant_authority=True if ba else None,
        bant_need=True if bn else None,bant_timeline=True if bt else None,limit=500)

    st.divider()
    rc1,rc2,rc3,rc4 = st.columns(4)
    with rc1: st.metric("🎯 Leads Found",len(results))
    with rc2: st.metric("✅ Qualified",sum(1 for r in results if r["qualification_status"]=="qualified"))
    with rc3: st.metric("📊 Avg Score",f'{sum(r["score"] for r in results)/len(results):.0f}' if results else "—")
    with rc4: st.metric("🏢 Companies",len(set(r["company_name"] for r in results)))

    if not results: st.info("No leads match. Adjust filters."); return

    a1,a2,a3,a4 = st.columns(4)
    with a1:
        sel = st.selectbox("Select",["All leads","Qualified only","Top 10","Top 25","Top 50"],key="gsel")
        chosen = (results if sel=="All leads" else
                  [r for r in results if r["qualification_status"]=="qualified"] if sel=="Qualified only" else
                  results[:10] if sel=="Top 10" else results[:25] if sel=="Top 25" else results[:50])
    with a2: vendor = st.selectbox("Assign Vendor",["Apollo","Hunter.io","Crunchbase","LinkedIn Sales Nav","Manual"],key="gv")
    with a3: campaign = st.text_input("Campaign Tag",value="Q1-2026-outbound",key="gc")
    with a4:
        st.markdown("&nbsp;")
        if st.button("🚀 Import Selected Leads",type="primary",use_container_width=True):
            st.success(f"✅ **{len(chosen)} leads** imported · Vendor: **{vendor}** · Campaign: **{campaign}**")

    # Results table
    tbl = [{"Score":round(r["score"]),"Status":r["qualification_status"].title(),
            "Company":r["company_name"],"Contact":r["contact_name"],"Title":r["contact_title"],
            "Market":f'{FLAGS.get(r["country"],"🌐")} {r["country"]}',
            "Industry":r["industry"],"Revenue":fmtr(r["revenue_usd"]),
            "BANT":("B" if r["budget_signal"] else "·")+("A" if r["authority_signal"] else "·")+
                   ("N" if r["need_signal"] else "·")+("T" if r["timeline_signal"] else "·")}
           for r in chosen[:100]]
    st.dataframe(tbl,use_container_width=True,hide_index=True,height=400)

    e1,e2,_ = st.columns([1,1,4])
    with e1:
        if st.button("📧 Queue Outreach",use_container_width=True):
            st.info(f"📧 {sum(1 for r in chosen if r['qualification_status'] in ['qualified','nurture'])} leads queued.")
    with e2:
        out=io.StringIO()
        w=csv.DictWriter(out,fieldnames=["company_name","contact_name","contact_title","email","score","qualification_status","industry","country","revenue_usd"])
        w.writeheader()
        for r in chosen: w.writerow({k:r.get(k,"") for k in w.fieldnames})
        st.download_button("📥 Export CSV",out.getvalue(),file_name=f"leads_{campaign}.csv",mime="text/csv",use_container_width=True)
    _footer()


# ══════════════════════════════════════════════════════
# 3. LEAD INTELLIGENCE
# ══════════════════════════════════════════════════════
def render_lead_intelligence(db,stats):
    st.markdown("## 🔍 Lead Intelligence")
    st.caption("Search and explore all scored leads")
    search = st.text_input("🔎",placeholder="Search company, contact, industry, title...",label_visibility="collapsed")
    with st.sidebar:
        st.divider(); st.markdown("### 🎛️ Filters")
        mkts=db.get_unique_values("country","dim_companies")
        fm=st.multiselect("Market",[f"{FLAGS.get(m,'🌐')} {m}" for m in mkts],key="fm")
        fmc=[m.split(" ")[-1] for m in fm] if fm else None
        fi=st.multiselect("Industry",db.get_unique_values("industry","dim_companies"),key="fi") or None
        scr=st.slider("Score",0,100,(0,100),key="scr")
        fst=st.multiselect("Status",["qualified","nurture","disqualified"],key="fst") or None
        fsen=st.multiselect("Seniority",db.get_unique_values("seniority","dim_contacts"),key="fsen2") or None
        # Sales Rep filter for Lead Intelligence
        li_rep = st.selectbox("👤 Sales Rep", ["All Reps"] + SDR_NAMES, key="li_rep")
    results = db.search_leads(text_query=search,markets=fmc,industries=fi,
        score_min=scr[0] if scr[0]>0 else None,score_max=scr[1] if scr[1]<100 else None,
        statuses=fst,seniorities=fsen,limit=200)

    # Assign reps deterministically to leads for filtering
    if results:
        for i, r in enumerate(results):
            r["assigned_rep"] = SDR_NAMES[i % len(SDR_NAMES)]
        if li_rep != "All Reps":
            results = [r for r in results if r["assigned_rep"] == li_rep]

    st.divider(); st.markdown(f"**{len(results)} leads found**")
    if not results: st.info("No leads match."); return

    def open_lead_in_nav(lead_id):
        st.session_state["open_lead_id"] = lead_id
        st.session_state["nav_radio"] = "🧭 Sales Navigator"

    # Print Table Headers
    with st.container():
        hc = st.columns([0.8, 2, 2, 1.5, 1, 1, 1, 1.2])
        headers = ["Score", "Company", "Contact", "Market / Industry", "BANT", "Stage", "Owner", "Action"]
        for col, title in zip(hc, headers):
            with col: st.markdown(f"<div style='font-size:0.8rem;text-transform:uppercase;color:#94a3b8;font-weight:700;margin-bottom:8px;'>{title}</div>", unsafe_allow_html=True)

    # Display leads with "Open in Navigator" button
    for i, r in enumerate(results[:50]):
        if i > 0:
            st.markdown("<hr style='margin:0.2em 0; border:none; border-top:1px solid #334155;'/>", unsafe_allow_html=True)
        with st.container():
            cols = st.columns([0.8, 2, 2, 1.5, 1, 1, 1, 1.2])
            with cols[0]:
                reasons = "&#10;• ".join(r.get("score_breakdown", {}).get("reasons", []))
                tooltip = f"AI Score Factors:&#10;• {reasons}" if reasons else "Score Breakdown Unavailable"
                st.markdown(f"<div title='{tooltip}' style='display:flex;align-items:center;gap:6px;height:100%;font-weight:700;cursor:help;'><span>{score_text(r['score'])[0]}</span><span>{score_text(r['score'])[2:]}</span></div>", unsafe_allow_html=True)
            with cols[1]: st.markdown(f"**{r['company_name']}**")
            with cols[2]: st.markdown(f"{r['contact_name']} · {r['contact_title'][:30]}")
            with cols[3]: st.markdown(f"{FLAGS.get(r['country'],'🌐')} {r['industry'][:20]}")
            with cols[4]:
                bant = ('B' if r['budget_signal'] else '·')+('A' if r['authority_signal'] else '·')+('N' if r['need_signal'] else '·')+('T' if r['timeline_signal'] else '·')
                st.markdown(f"`{bant}`")
            with cols[5]: st.markdown(f"📊 {r['deal_stage'][:12]}" if r.get('deal_stage') else "—")
            with cols[6]: st.markdown(f"👤 {r['assigned_rep'].split()[0]}")
            with cols[7]:
                st.button("🧭 Open", key=f"nav_{r['lead_id']}", use_container_width=True, on_click=open_lead_in_nav, args=(r['lead_id'],))
    _footer()


# ══════════════════════════════════════════════════════
# 4. SALES NAVIGATOR
# ══════════════════════════════════════════════════════
def render_sales_navigator(db,stats):
    st.markdown("## 🧭 Sales Navigator")
    st.caption("Deep-dive: enrichment, BANT, call plan, outreach cadence")
    leads=db.search_leads(limit=500)
    if not leads: st.warning("No scored leads."); return
    opts={f"{score_text(l['score'])} {l['company_name']} — {l['contact_name']}":l["lead_id"] for l in leads}

    # Check if a lead was opened from Lead Intelligence
    pre_selected_id = st.session_state.get("open_lead_id", None)

    with st.sidebar:
        st.divider(); st.markdown("### 🧭 Select Lead")
        ns=st.text_input("Filter...",key="ns",placeholder="Type...")
        filtered={k:v for k,v in opts.items() if ns.lower() in k.lower()} if ns else opts
        if not filtered: st.warning("No match."); return

        # If pre-selected from Lead Intelligence, find and select it
        default_idx = 0
        if pre_selected_id:
            for i, (label, lid) in enumerate(filtered.items()):
                if lid == pre_selected_id:
                    default_idx = i; break
            st.session_state.pop("open_lead_id", None)

        sel_label=st.selectbox("Choose",list(filtered.keys()),index=default_idx,label_visibility="collapsed")
        sel_id=filtered[sel_label]
    lead=db.get_lead_detail(sel_id)
    if not lead: st.error("Not found."); return

    # Assign rep deterministically
    lead_idx = list(opts.values()).index(sel_id) if sel_id in opts.values() else 0
    assigned_rep = SDR_NAMES[lead_idx % len(SDR_NAMES)]

    st.divider()
    h1,h2,h3 = st.columns([3,2,1])
    with h1:
        st.markdown(f"### 🏢 {lead['company_name']}")
        st.markdown(f"{FLAGS.get(lead['country'],'🌐')} {lead['country']}, {lead['state']} · **{lead['industry']}** · {lead.get('funding_stage','')}")
        st.markdown(f"💰 **{fmtr(lead['revenue_usd'])}** · 👥 **{lead['employee_count']}** emp")
    with h2:
        st.markdown(f"### 👤 {lead['contact_name']}")
        st.markdown(f"**{lead['contact_title']}** · {lead.get('department','')}")
        st.markdown(f"📧 {lead.get('email','')}");
        if lead.get("phone"): st.markdown(f"📞 {lead['phone']}")
    with h3:
        s=lead["score"]; c="#22c55e" if s>=80 else ("#eab308" if s>=60 else "#ef4444")
        st.markdown(f'<div style="text-align:center;padding:20px;background:linear-gradient(145deg,rgba(15,20,35,0.9),rgba(20,28,50,0.85));border-radius:16px;border:2px solid {c};"><div style="font-size:2.8em;font-weight:900;color:{c};">{s:.0f}</div><div style="font-size:.8em;color:#64748b;text-transform:uppercase;">{lead["qualification_status"].title()}</div></div>',unsafe_allow_html=True)

    # Rep owner + Funnel Phase + Action buttons
    info1, info2, info3 = st.columns(3)
    with info1:
        st.markdown(f'👤 **Sales Rep:** {assigned_rep}')
    with info2:
        stage = lead.get("deal_stage", "New Lead")
        stage_colors = {"qualified":"🟢","nurture":"🟡","disqualified":"🔴","new":"⚪"}
        dot = stage_colors.get(lead.get("qualification_status",""), "⚪")
        st.markdown(f'{dot} **Stage:** {stage}')
    with info3:
        st.markdown(f'🎯 **Status:** {lead["qualification_status"].title()}')

    st.markdown("<br/>", unsafe_allow_html=True)
    btn1, btn2, btn3, btn4, btn5 = st.columns(5)
    with btn1:
        email = lead.get('email', '')
        if st.button("📧 Send Email", use_container_width=True, key="send_email"):
            if email:
                st.markdown(f'<meta http-equiv="refresh" content="0;url=mailto:{email}?subject=Follow%20Up%20-%20{lead["company_name"]}">',unsafe_allow_html=True)
            else: st.warning("No email on file")
    with btn2:
        phone = lead.get('phone', '')
        if st.button("📱 WhatsApp", use_container_width=True, key="send_wa"):
            if phone:
                clean_phone = phone.replace(' ','').replace('-','').replace('+','')
                st.markdown(f'<meta http-equiv="refresh" content="0;url=https://wa.me/{clean_phone}?text=Hi%20{lead["contact_name"].split()[0]}%2C%20following%20up%20regarding%20{lead["company_name"]}">',unsafe_allow_html=True)
            else: st.warning("No phone on file")
    with btn3:
        # Mock linkedin URL
        li_url = f"https://www.linkedin.com/search/results/people/?keywords={lead['contact_name'].replace(' ','%20')}%20{lead['company_name'].replace(' ','%20')}"
        st.link_button("💼 Send LinkedIn", url=li_url, use_container_width=True)
    with btn4:
        st.link_button("🌐 Company Website", url=f"https://www.{lead['company_name'].lower().replace(' ','')}.com", use_container_width=True)
    with btn5:
        st.link_button("🔗 Company LinkedIn", url=f"https://www.linkedin.com/company/{lead['company_name'].lower().replace(' ','-')}", use_container_width=True)

    st.divider()
    st.markdown('<div class="section-header">🎯 BANT QUALIFICATION</div>',unsafe_allow_html=True)
    bant=[("💰 Budget",lead["budget_signal"],f"Rev: {fmtr(lead['revenue_usd'])} | {lead.get('funding_stage','')}"),
          ("👑 Authority",lead["authority_signal"],f"{lead.get('seniority','')}: {lead['contact_title']}"),
          ("🎯 Need",lead["need_signal"],f"Gaps: {', '.join((lead.get('tech_stack_gaps') or [])[:3]) or 'None'}"),
          ("⏰ Timeline",lead["timeline_signal"],"Active buying signals")]
    bcols=st.columns(4)
    for col,(label,sig,detail) in zip(bcols,bant):
        with col:
            ic="✅" if sig else "❌"; cr="#10b981" if sig else "#ef4444"
            st.markdown(f'<div style="background:linear-gradient(145deg,rgba(15,20,35,0.7),rgba(20,28,50,0.6));padding:18px;border-radius:14px;border:1px solid {cr}40;text-align:center;"><div style="font-size:2em;">{ic}</div><div style="font-weight:800;color:#f8fafc;margin:6px 0;">{label}</div><div style="font-size:.75em;color:#94a3b8;">{detail}</div></div>',unsafe_allow_html=True)
    st.divider()
    lc,rc=st.columns(2)
    with lc:
        st.markdown('<div class="section-header">🔬 ENRICHMENT DATA</div>',unsafe_allow_html=True)
        st.markdown("**Tech Stack**"); st.markdown("".join(f'<span class="tag">{t}</span>' for t in (lead.get("tech_stack_detected") or [])) or "_None_",unsafe_allow_html=True)
        st.markdown("**Tech Gaps**"); st.markdown("".join(f'<span class="signal-tag">⚡ {g}</span>' for g in (lead.get("tech_stack_gaps") or [])) or "_None_",unsafe_allow_html=True)
        st.markdown("**Buying Signals**")
        for sig in (lead.get("buying_signals") or []): st.markdown(f"- 📡 {sig}")
        comp=(lead.get("enrichment_completeness") or 0)*100; st.progress(comp/100,f"Enrichment: {comp:.0f}%")
    with rc:
        st.markdown('<div class="section-header">📞 DEAL BRIEF</div>',unsafe_allow_html=True)
        if lead.get("deal_brief"): st.code(lead["deal_brief"],language="text")
        else: st.info("No brief — only qualified/nurture leads get briefs.")
    st.divider()
    st.markdown('<div class="section-header">📧 OUTREACH CADENCE</div>',unsafe_allow_html=True)
    events=lead.get("outreach_events",[])
    if events:
        for ev in sorted(events,key=lambda e:e["sequence_step"]):
            css="done" if ev.get("opened_at") else ("active" if ev["status"]=="sent" else "")
            icon="📖" if ev.get("opened_at") else ("📤" if ev["status"]=="sent" else "⏳")
            resp=""
            if ev.get("response_type"):
                rc2="#22c55e" if ev["response_type"]=="interested" else "#ef4444"
                resp=f' → <span style="color:{rc2};font-weight:700;">{ev["response_type"].replace("_"," ").title()}</span>'
            st.markdown(f'<div class="timeline-item {css}"><strong>Touch {ev["sequence_step"]}</strong> {icon}{resp}<br/><span style="color:#64748b;font-size:.82em;">{ev.get("subject","")}</span></div>',unsafe_allow_html=True)
    else: st.info("No outreach events.")
    _footer()


# ══════════════════════════════════════════════════════
# 5. CRM / SALESFORCE OPPORTUNITIES
# ══════════════════════════════════════════════════════
def render_crm(sim,pm,period,start_date=None,end_date=None,rep_name=None):
    opps = list(sim["sfdc"])  # copy so we don't mutate
    st.markdown("## 💼 CRM / Salesforce Opportunities")
    date_banner(period, pm)

    # Filter opportunities by date range
    if start_date and end_date:
        sd = str(start_date); ed = str(end_date)
        opps = [o for o in opps if o["created_date"] <= ed and o["close_date"] >= sd]

    # Filter by rep
    if rep_name:
        opps = [o for o in opps if o["owner"] == rep_name]

    # KPIs
    open_opps = [o for o in opps if o["stage"] not in ("Closed Won","Closed Lost")]
    won = [o for o in opps if o["stage"]=="Closed Won"]
    lost = [o for o in opps if o["stage"]=="Closed Lost"]
    at_risk = [o for o in opps if o["is_at_risk"]]
    stalled = [o for o in opps if o["is_stalled"]]
    total_open = sum(o["amount"] for o in open_opps)
    total_weighted = sum(o["weighted_amount"] for o in open_opps)
    total_won = sum(o["amount"] for o in won)

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.metric("📂 OPEN OPPS",len(open_opps))
    with k2: st.metric("💰 OPEN VALUE",fmtr(total_open))
    with k3: st.metric("📊 WEIGHTED",fmtr(total_weighted))
    with k4: st.metric("🏆 WON",f"{len(won)} ({fmtr(total_won)})")
    with k5: st.metric("❌ LOST",len(lost))
    with k6: st.metric("⚠️ AT RISK",len(at_risk),f"{len(stalled)} stalled")

    st.divider()

    # Pipeline by Stage + Deal Aging
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### 📊 Pipeline by Stage")
        stage_order=["Discovery","Qualification","Demo/POC","Proposal Sent","Negotiation","Verbal Commit","Closed Won","Closed Lost"]
        stage_vals={s:sum(o["amount"] for o in opps if o["stage"]==s) for s in stage_order}
        stage_counts={s:sum(1 for o in opps if o["stage"]==s) for s in stage_order}
        fig = go.Figure(go.Bar(
            y=list(stage_vals.keys()),x=list(stage_vals.values()),orientation="h",
            text=[f'{fmtr(v)} ({stage_counts[s]} deals)' for s,v in stage_vals.items()],textposition="auto",
            marker_color=["#e94560","#c33b54","#a855f7","#6366f1","#3b82f6","#22c55e","#10b981","#ef4444"]))
        fig.update_layout(**PL,height=380,yaxis=dict(autorange="reversed"),xaxis_title="Value ($)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### ⏱️ Deal Aging (Days Open)")
        open_sorted = sorted(open_opps,key=lambda o:o["age_days"],reverse=True)
        colors = ["#ef4444" if o["age_days"]>45 else "#eab308" if o["age_days"]>30 else "#22c55e" for o in open_sorted]
        fig = go.Figure(go.Bar(
            y=[o["company"] for o in open_sorted],x=[o["age_days"] for o in open_sorted],
            orientation="h",marker_color=colors,
            text=[f'{o["age_days"]}d · {o["stage"]}' for o in open_sorted],textposition="auto"))
        fig.add_vline(x=30,line_dash="dash",line_color="#eab308",annotation_text="30d target")
        fig.update_layout(**PL,height=380,yaxis=dict(autorange="reversed"),xaxis_title="Days")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Expected Close This Quarter
    st.markdown("### 📅 Expected Close Dates")
    closing_soon = sorted([o for o in open_opps],key=lambda o:o["close_date"])
    opp_tbl = []
    for o in closing_soon:
        risk = ""
        if o["is_at_risk"]: risk = '<span class="risk-badge">AT RISK</span>'
        elif o["is_stalled"]: risk = '<span class="stalled-badge">STALLED</span>'
        opp_tbl.append({
            "ID":o["opp_id"],"Company":o["company"],"Stage":o["stage"],
            "Amount":fmtr(o["amount"]),"Weighted":fmtr(o["weighted_amount"]),
            "Prob":f'{o["probability"]*100:.0f}%',"Owner":o["owner"],
            "Close Date":o["close_date"],"Age":f'{o["age_days"]}d',
            "Last Activity":o["last_activity"],"Next Step":o["next_step"]})
    st.dataframe(opp_tbl,use_container_width=True,hide_index=True,height=450)

    st.divider()

    # Win/Loss + Owner Pipeline
    w1,w2 = st.columns(2)
    with w1:
        st.markdown("### 🎯 Win/Loss Analysis")
        labels=["Won","Open","Lost"]; vals=[len(won),len(open_opps),len(lost)]
        fig = go.Figure(go.Pie(labels=labels,values=vals,hole=.55,
            marker=dict(colors=["#22c55e","#6366f1","#ef4444"]),textinfo="label+value"))
        fig.update_layout(**PL,height=300,showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with w2:
        st.markdown("### 👤 Pipeline by Owner")
        owner_pipe = {}
        for o in open_opps:
            owner_pipe[o["owner"]] = owner_pipe.get(o["owner"],0) + o["amount"]
        sorted_owners = sorted(owner_pipe.items(),key=lambda x:x[1],reverse=True)
        fig = go.Figure(go.Bar(
            y=[o[0] for o in sorted_owners[::-1]],x=[o[1] for o in sorted_owners[::-1]],
            orientation="h",marker_color="#a855f7",
            text=[fmtr(o[1]) for o in sorted_owners[::-1]],textposition="auto"))
        fig.update_layout(**PL,height=300,xaxis_title="Pipeline ($)")
        st.plotly_chart(fig, use_container_width=True)
    _footer()


# ══════════════════════════════════════════════════════
# 6. PIPELINE ANALYTICS
# ══════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════
def render_pipeline_analytics(db,stats,sim,pm,period,current=None,rep_name=None):
    st.markdown("## 📈 Pipeline Analytics")
    date_banner(period, pm)

    k1,k2,k3,k4,k5=st.columns(5)
    with k1: st.metric("📥 LEADS",fmtn(pm["total_leads"]),dstr(pm["leads_delta"],pm["has_comparison"]))
    with k2: st.metric("✅ QUALIFIED",fmtn(pm["total_qualified"]),dstr(pm["qual_delta"],pm["has_comparison"]))
    with k3: st.metric("📅 MEETINGS",fmtn(pm["total_meetings"]),dstr(pm["meetings_delta"],pm["has_comparison"]))
    with k4: st.metric("🤝 DEALS",fmtn(pm["total_deals"]),dstr(pm["deals_delta"],pm["has_comparison"]))
    with k5: st.metric("📊 CONVERSION",f'{pm["conversion_rate"]:.1f}%')
    st.divider()

    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 📊 Conversion Waterfall")
        fig=go.Figure(go.Waterfall(x=["Leads","Qualified","Meetings","Deals"],
            y=[pm["total_leads"],pm["total_qualified"],pm["total_meetings"],pm["total_deals"]],
            textposition="auto",connector=dict(line=dict(color="rgba(148,163,184,0.15)")),
            decreasing=dict(marker=dict(color="#f43f5e")),increasing=dict(marker=dict(color="#10b981")),
            totals=dict(marker=dict(color="#6366f1"))))
        fig.update_layout(**PL,height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### ⏱️ Stage Velocity (Avg Days)")
        base_vel = sim["velocity"]
        dynamic_vel = []

        # Make velocity dynamic based on rep performance and period deals
        modifier = 1.0
        if rep_name and rep_name in SDR_NAMES:
            rep_idx = SDR_NAMES.index(rep_name)
            # Top reps (low idx) close faster (lower days)
            modifier = 0.75 + (rep_idx * 0.08)
        
        # Add variance based on the date range metrics to simulate period shifts
        period_variance = 1.0 + ((pm.get("total_deals", 0) % 7) - 3) * 0.04

        for v in base_vel:
            new_days = round(v["avg_days"] * modifier * period_variance, 1)
            new_days = max(1.0, new_days)  # Prevent zero or negative
            dynamic_vel.append({
                "stage": v["stage"],
                "avg_days": new_days,
                "target_days": v["target_days"]
            })

        colors=["#10b981" if v["avg_days"]<=v["target_days"] else "#f43f5e" for v in dynamic_vel]
        fig=go.Figure()
        fig.add_trace(go.Bar(y=[v["stage"] for v in dynamic_vel],x=[v["avg_days"] for v in dynamic_vel],orientation="h",
            marker_color=colors,name="Actual",text=[f'{v["avg_days"]}d (tgt: {v["target_days"]}d)' for v in dynamic_vel],textposition="auto"))
        fig.add_trace(go.Scatter(y=[v["stage"] for v in dynamic_vel],x=[v["target_days"] for v in dynamic_vel],mode="markers",
            marker=dict(symbol="line-ns",size=20,color="#cbd5e1",line_width=2),name="Target"))
        fig.update_layout(**PL,height=380,yaxis=dict(autorange="reversed"),xaxis_title="Days",
                          legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    st.markdown("### 🎯 Campaign Attribution & ROI")
    camps=sim["campaigns"]
    camp_tbl=[{"Campaign":c["name"],"Channel":c["channel"],"Spend":fmtr(c["spend"]),
               "Leads":c["leads"],"Qualified":c["qualified"],"Deals":c["deals"],
               "Revenue":fmtr(c["revenue"]),"CPL":f'${c["cpl"]:.0f}',"ROI":f'{c["roi"]:.0f}%'}
              for c in sorted(camps,key=lambda x:x["revenue"],reverse=True)]
    st.dataframe(camp_tbl,use_container_width=True,hide_index=True,height=340)
    st.divider()

    st.markdown("### 🏅 SDR Leaderboard")
    sdr=sim["sdr"]
    l1,l2=st.columns([3,2])
    with l1:
        sdr_tbl=[{"#":i+1,"":("🟢" if s["attainment"]>=100 else "🟡" if s["attainment"]>=70 else "🔴"),
                  "SDR":s["name"],"Meetings":s["meetings_booked"],"Pipeline":fmtr(s["pipeline_generated"]),
                  "Quota":f'{s["attainment"]}%',"📧/d":s["emails_per_day"],"📞/d":s["calls_per_day"],
                  "📅/wk":s["meetings_per_week"]} for i,s in enumerate(sdr)]
        st.dataframe(sdr_tbl,use_container_width=True,hide_index=True)
    with l2:
        fig=go.Figure(go.Bar(y=[s["name"] for s in sdr[::-1]],x=[s["pipeline_generated"] for s in sdr[::-1]],
            orientation="h",marker=dict(color=["#22c55e" if s["attainment"]>=100 else "#eab308" if s["attainment"]>=70 else "#ef4444" for s in sdr[::-1]]),
            text=[f'{s["attainment"]}%' for s in sdr[::-1]],textposition="auto"))
        fig.add_vline(x=250000,line_dash="dash",line_color="#f1f5f9",annotation_text="$250K Quota")
        fig.update_layout(**PL,height=350,xaxis_title="Pipeline ($)")
        st.plotly_chart(fig, use_container_width=True)
    _footer()


# ══════════════════════════════════════════════════════
# 7. OUTREACH PERFORMANCE
# ══════════════════════════════════════════════════════
def render_outreach(db,stats,sim,pm,period,current=None):
    st.markdown("## 📧 Outreach Performance")
    date_banner(period, pm)

    # Use period-filtered email metrics from pm
    sent = pm["total_emails"]; opened = pm["total_opened"]; replied = pm["total_replied"]
    interested = int(replied * 0.45)  # ~45% of replies are interested

    k1,k2,k3,k4,k5,k6=st.columns(6)
    with k1: st.metric("📤 SENT",fmtn(sent))
    with k2: st.metric("📖 OPENED",fmtn(opened),f"{opened/sent*100:.0f}%" if sent else "—")
    with k3: st.metric("💬 REPLIED",fmtn(replied),f"{replied/sent*100:.0f}%" if sent else "—")
    with k4: st.metric("🤝 INTERESTED",fmtn(interested))
    with k5: st.metric("📅 MEETINGS",fmtn(pm["total_meetings"]))
    with k6: st.metric("⚡ VELOCITY",f'{pm["sales_velocity"]/1000:.0f}K/d')
    st.divider()

    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 📊 Engagement by Touch")
        events=db.get_outreach_events(limit=2000)
        if events:
            d={"Touch":[],"Sent":[],"Opened":[],"Replied":[]}
            for step in [1,2,3]:
                se=[e for e in events if e.sequence_step==step]
                d["Touch"].append(f"Touch {step}"); d["Sent"].append(len(se))
                d["Opened"].append(sum(1 for e in se if e.opened_at))
                d["Replied"].append(sum(1 for e in se if e.responded_at))
            fig=go.Figure()
            fig.add_trace(go.Bar(name="Sent",x=d["Touch"],y=d["Sent"],marker_color="rgba(233,69,96,0.5)"))
            fig.add_trace(go.Bar(name="Opened",x=d["Touch"],y=d["Opened"],marker_color="rgba(234,179,8,0.6)"))
            fig.add_trace(go.Bar(name="Replied",x=d["Touch"],y=d["Replied"],marker_color="rgba(34,197,94,0.7)"))
            fig.update_layout(**PL,height=350,barmode="group")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("### 💬 Response Types")
        if events:
            rc={}
            for e in events:
                if e.response_type:
                    rt=e.response_type.value.replace("_"," ").title(); rc[rt]=rc.get(rt,0)+1
            if rc:
                cmap={"Interested":"#22c55e","More Info":"#eab308","Not Interested":"#ef4444","Not Now":"#64748b"}
                fig=go.Figure(go.Pie(labels=list(rc.keys()),values=list(rc.values()),hole=.55,
                    marker=dict(colors=[cmap.get(k,"#64748b") for k in rc])))
                fig.update_layout(**PL,height=350,showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
    st.divider()

    st.markdown("### 📈 Weekly Email Trend")
    weekly = aggregate_weekly(current) if current else sim["weekly"]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[w["start_date"] for w in weekly],y=[w["emails_sent"] for w in weekly],
        name="Sent",line=dict(color="#e94560",width=2),fill="tozeroy",fillcolor="rgba(233,69,96,0.05)"))
    fig.add_trace(go.Scatter(x=[w["start_date"] for w in weekly],y=[w["emails_opened"] for w in weekly],
        name="Opened",line=dict(color="#eab308",width=2)))
    fig.add_trace(go.Scatter(x=[w["start_date"] for w in weekly],y=[w["emails_replied"] for w in weekly],
        name="Replied",line=dict(color="#22c55e",width=2)))
    fig.update_layout(**PL,height=350,legend=dict(orientation="h",y=1.12))
    st.plotly_chart(fig, use_container_width=True)
    _footer()


if __name__=="__main__":
    main()
