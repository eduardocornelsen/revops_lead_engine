"""
i18n.py — Internationalisation for LeadEngine RevOps Dashboard
Supported languages: EN (English) | PT (Português)
"""
from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── App-level ────────────────────────────────────────────────────────────
    "app_title": {
        "EN": "LeadEngine RevOps",
        "PT": "LeadEngine RevOps",
    },
    "app_subtitle": {
        "EN": "RevOps Command Center",
        "PT": "Central de Comando RevOps",
    },
    "lang_toggle_label": {
        "EN": "🇧🇷 PT",
        "PT": "🇺🇸 EN",
    },

    # ── Navigation ───────────────────────────────────────────────────────────
    "nav_copilot":    {"EN": "AI RevOps Copilot",   "PT": "Copiloto IA RevOps"},
    "nav_revenue":    {"EN": "Revenue Dashboard",    "PT": "Painel de Receita"},
    "nav_leads":      {"EN": "Generate Leads",       "PT": "Gerar Leads"},
    "nav_intel":      {"EN": "Lead Intelligence",    "PT": "Inteligência de Leads"},
    "nav_navigator":  {"EN": "Sales Navigator",      "PT": "Navegador de Vendas"},
    "nav_crm":        {"EN": "CRM / Salesforce",     "PT": "CRM / Salesforce"},
    "nav_pipeline":   {"EN": "Pipeline Analytics",   "PT": "Analytics de Pipeline"},
    "nav_outreach":   {"EN": "Outreach",             "PT": "Prospecção"},
    "nav_postsales":  {"EN": "Post-Sales (NDR)",     "PT": "Pós-Venda (NDR)"},
    "nav_scenario":   {"EN": "Scenario Modeler",     "PT": "Modelador de Cenários"},

    # ── Filter bar ───────────────────────────────────────────────────────────
    "filter_label":     {"EN": "🔽 Filters",            "PT": "🔽 Filtros"},
    "filter_from":      {"EN": "📅 From",               "PT": "📅 De"},
    "filter_to":        {"EN": "📅 To",                 "PT": "📅 Até"},
    "filter_period":    {"EN": "Period",                "PT": "Período"},
    "filter_reset":     {"EN": "🔄 Reset",              "PT": "🔄 Resetar"},
    "filter_rep":       {"EN": "👤 Sales Rep",          "PT": "👤 Representante"},
    "filter_whole_team":{"EN": "🏢 Whole Team",         "PT": "🏢 Equipe Toda"},
    "period_custom":    {"EN": "Custom",                "PT": "Personalizado"},
    "period_30d":       {"EN": "Last 30 Days",          "PT": "Últimos 30 Dias"},
    "period_60d":       {"EN": "Last 60 Days",          "PT": "Últimos 60 Dias"},
    "period_quarter":   {"EN": "Full Quarter",          "PT": "Trimestre Completo"},
    "period_year":      {"EN": "Last Year",             "PT": "Último Ano"},

    # ── Revenue Dashboard ────────────────────────────────────────────────────
    "page_revenue":         {"EN": "Revenue Dashboard",       "PT": "Painel de Receita"},
    "revenue_caption":      {"EN": "Executive overview of revenue, pipeline coverage, and sales engine performance.", "PT": "Visão executiva de receitas, cobertura de pipeline e performance do motor de vendas."},
    "section_exec_health":  {"EN": "📈 Executive Health",     "PT": "📈 Saúde Executiva"},
    "section_sales_engine": {"EN": "⚡ Sales Engine",         "PT": "⚡ Motor de Vendas"},
    "metric_revenue":       {"EN": "💰 REVENUE",              "PT": "💰 RECEITA"},
    "metric_pipeline":      {"EN": "📊 PIPELINE",             "PT": "📊 PIPELINE"},
    "metric_quota":         {"EN": "🎯 QUOTA",                "PT": "🎯 QUOTA"},
    "metric_coverage":      {"EN": "📈 COVERAGE",             "PT": "📈 COBERTURA"},
    "metric_leads":         {"EN": "📥 LEADS",                "PT": "📥 LEADS"},
    "metric_qualified":     {"EN": "✅ QUALIFIED",            "PT": "✅ QUALIFICADOS"},
    "metric_meetings":      {"EN": "📅 MEETINGS",             "PT": "📅 REUNIÕES"},
    "metric_deals":         {"EN": "🤝 DEALS WON",            "PT": "🤝 NEGÓCIOS GANHOS"},
    "metric_win_rate":      {"EN": "🏆 WIN RATE",             "PT": "🏆 TAXA DE GANHO"},
    "metric_cycle":         {"EN": "⏱️ CYCLE",               "PT": "⏱️ CICLO"},
    "metric_target":        {"EN": "Target",                  "PT": "Meta"},
    "metric_coverage_ok":   {"EN": "🟢 OK",                  "PT": "🟢 OK"},
    "metric_coverage_low":  {"EN": "🔴 Low",                  "PT": "🔴 Baixo"},
    "section_quota":        {"EN": "🎯 Quota Attainment",     "PT": "🎯 Atingimento de Quota"},
    "quota_of_target":      {"EN": "of {target} target",      "PT": "de {target} de meta"},
    "section_risk_alerts":  {"EN": "🚨 Risk Alerts",          "PT": "🚨 Alertas de Risco"},
    "section_unit_econ":    {"EN": "💲 Unit Economics",       "PT": "💲 Economics Unitários"},
    "metric_cac":           {"EN": "Customer Acquisition Cost","PT": "Custo de Aquisição (CAC)"},
    "metric_ltv":           {"EN": "Lifetime Value",          "PT": "Valor Vitalício (LTV)"},
    "metric_ltv_cac":       {"EN": "LTV : CAC Ratio",         "PT": "Proporção LTV : CAC"},
    "metric_ad_spend":      {"EN": "Total Ad Spend",          "PT": "Investimento em Anúncios"},

    # ── Alert types ──────────────────────────────────────────────────────────
    "alert_below_quota":       {"EN": "Below Quota",          "PT": "Abaixo da Quota"},
    "alert_quota_risk":        {"EN": "Quota at Risk",        "PT": "Quota em Risco"},
    "alert_quota_exceeded":    {"EN": "Quota Exceeded",       "PT": "Quota Superada"},
    "alert_low_coverage":      {"EN": "Low Coverage",         "PT": "Cobertura Baixa"},
    "alert_low_win_rate":      {"EN": "Low Win Rate",         "PT": "Taxa de Ganho Baixa"},
    "alert_strong_conversion": {"EN": "Strong Conversion",    "PT": "Conversão Forte"},
    "alert_healthy_econ":      {"EN": "Healthy Unit Economics","PT": "Economics Saudáveis"},

    # ── Revenue charts ───────────────────────────────────────────────────────
    "chart_rev_pipeline_trend":  {"EN": "📈 Revenue & Pipeline Trend", "PT": "📈 Tendência Receita & Pipeline"},
    "chart_view_by":             {"EN": "View by",             "PT": "Ver por"},
    "chart_cumulative":          {"EN": "Cumulative",          "PT": "Acumulado"},
    "chart_show_pipeline":       {"EN": "Show Pipeline",       "PT": "Mostrar Pipeline"},
    "chart_revenue_trace":       {"EN": "Revenue",             "PT": "Receita"},
    "chart_cum_revenue":         {"EN": "Cumulative Revenue",  "PT": "Receita Acumulada"},
    "chart_pipeline_eop":        {"EN": "Pipeline (End of Period)", "PT": "Pipeline (Fim do Período)"},
    "chart_cum_target":          {"EN": "Cumulative Target",   "PT": "Meta Acumulada"},
    "chart_lead_funnel":         {"EN": "Lead Funnel & Conversion", "PT": "Funil de Leads & Conversão"},
    "funnel_leads":              {"EN": "Leads Generated",     "PT": "Leads Gerados"},
    "funnel_qualified":          {"EN": "Qualified",           "PT": "Qualificados"},
    "funnel_meetings":           {"EN": "Meetings",            "PT": "Reuniões"},
    "funnel_deals":              {"EN": "Deals Won",           "PT": "Negócios Ganhos"},
    "chart_forecast":            {"EN": "📊 Revenue Forecast", "PT": "📊 Previsão de Receita"},
    "chart_best_case":           {"EN": "Best Case",           "PT": "Melhor Cenário"},
    "chart_weighted":            {"EN": "Weighted",            "PT": "Ponderado"},
    "chart_total_pipeline":      {"EN": "Total Pipeline",      "PT": "Pipeline Total"},
    "chart_deals_in_pipe":       {"EN": "Deals in Pipe",       "PT": "Negócios no Pipe"},
    "chart_unweighted":          {"EN": "Unweighted",          "PT": "Não Ponderado"},
    "chart_agg_day":             {"EN": "Day",                 "PT": "Dia"},
    "chart_agg_week":            {"EN": "Week",                "PT": "Semana"},
    "chart_agg_month":           {"EN": "Month",               "PT": "Mês"},
    "chart_agg_quarter":         {"EN": "Quarter",             "PT": "Trimestre"},

    # ── Scenario Modeler ─────────────────────────────────────────────────────
    "page_scenario":            {"EN": "🔮 Revenue Scenario Modeler", "PT": "🔮 Modelador de Cenários de Receita"},
    "scenario_caption":         {"EN": "Adjust key levers below to instantly project end-of-quarter pipeline and revenue outcomes.",
                                 "PT": "Ajuste os alavancas abaixo para projetar instantaneamente os resultados de pipeline e receita do trimestre."},
    "section_levers":           {"EN": "🎛️ REVENUE LEVERS",    "PT": "🎛️ ALAVANCAS DE RECEITA"},
    "lever_leads":              {"EN": "Lead Volume Δ (%)",    "PT": "Volume de Leads Δ (%)"},
    "lever_win_rate":           {"EN": "Win Rate Δ (Abs %)",   "PT": "Taxa de Ganho Δ (%)"},
    "lever_acv":                {"EN": "ACV Δ (%)",            "PT": "ACV Δ (%)"},
    "lever_cycle":              {"EN": "Cycle Time Δ (Days)",  "PT": "Tempo de Ciclo Δ (Dias)"},
    "section_ai_insights":      {"EN": "🤖 AI SCENARIO INSIGHTS", "PT": "🤖 INSIGHTS DE CENÁRIO IA"},
    "section_projected":        {"EN": "📈 PROJECTED OUTCOMES", "PT": "📈 RESULTADOS PROJETADOS"},
    "proj_revenue":             {"EN": "Projected Revenue",    "PT": "Receita Projetada"},
    "proj_deals":               {"EN": "Projected Deals Won",  "PT": "Negócios Ganhos Projetados"},
    "proj_acv":                 {"EN": "Projected ACV",        "PT": "ACV Projetado"},
    "proj_velocity":            {"EN": "Projected Velocity",   "PT": "Velocidade Projetada"},
    "vs_baseline":              {"EN": "vs baseline",          "PT": "vs linha base"},
    "chart_target_quota":       {"EN": "Target Quota",         "PT": "Meta de Quota"},
    "chart_baseline_pace":      {"EN": "Baseline Pace",        "PT": "Ritmo Base"},
    "chart_projected_pace":     {"EN": "Projected Pace",       "PT": "Ritmo Projetado"},
    "chart_cum_pipeline_rev":   {"EN": "Cumulative Pipeline Revenue ($)", "PT": "Receita Acumulada do Pipeline ($)"},
    "chart_days_forward":       {"EN": "Days Forward (Next 90 Days)", "PT": "Dias à Frente (Próximos 90 Dias)"},
    "ai_attainable":            {"EN": "**Target Attainable:**", "PT": "**Meta Alcançável:**"},
    "ai_growth":                {"EN": "**Growth, but missing quota:**", "PT": "**Crescimento, mas abaixo da meta:**"},
    "ai_contraction":           {"EN": "**Severe Revenue Contraction:**", "PT": "**Contração Grave de Receita:**"},

    # ── Pipeline Analytics ───────────────────────────────────────────────────
    "page_pipeline":            {"EN": "📈 Pipeline Analytics",  "PT": "📈 Analytics de Pipeline"},
    "pipeline_caption":         {"EN": "Analyze conversion rates, sales velocity, and SDR leaderboard metrics.", "PT": "Analise taxas de conversão, velocidade de vendas e métricas do ranking de SDRs."},
    "metric_conversion":        {"EN": "📊 CONVERSION",          "PT": "📊 CONVERSÃO"},
    "chart_conv_waterfall":     {"EN": "### 📊 Conversion Waterfall", "PT": "### 📊 Funil de Conversão"},
    "chart_stage_velocity":     {"EN": "### ⏱️ Stage Velocity (Avg Days)", "PT": "### ⏱️ Velocidade por Estágio (Dias Médios)"},
    "chart_days_label":         {"EN": "Days",                   "PT": "Dias"},
    "chart_target_label":       {"EN": "Target",                 "PT": "Meta"},
    "chart_actual_label":       {"EN": "Actual",                 "PT": "Real"},
    "chart_camp_attribution":   {"EN": "### 🎯 Campaign Attribution & ROI", "PT": "### 🎯 Atribuição de Campanha & ROI"},
    "chart_pipeline_owner":     {"EN": "### 👤 Pipeline by Owner", "PT": "### 👤 Pipeline por Responsável"},
    "chart_pipeline_label":     {"EN": "Pipeline ($)",           "PT": "Pipeline (R$)"},
    "chart_sdr_leaderboard":    {"EN": "### 🏅 SDR Leaderboard", "PT": "### 🏅 Ranking de SDRs"},
    "chart_quota_label":        {"EN": "$250K Quota",            "PT": "Quota $250K"},

    # ── CRM / Salesforce ─────────────────────────────────────────────────────
    "page_crm":                 {"EN": "💼 CRM / Salesforce Opportunities", "PT": "💼 CRM / Oportunidades Salesforce"},
    "crm_caption":              {"EN": "Manage active opportunities, sort by deal value, and monitor close dates.", "PT": "Gerencie oportunidades ativas, ordene por valor do negócio e monitore as datas de fechamento."},
    "crm_open_opps":            {"EN": "🔄 OPEN OPPS",           "PT": "🔄 OPPS ABERTAS"},
    "crm_won":                  {"EN": "✅ WON",                 "PT": "✅ GANHOS"},
    "crm_lost":                 {"EN": "❌ LOST",                "PT": "❌ PERDIDOS"},
    "crm_at_risk":              {"EN": "⚠️ AT RISK",            "PT": "⚠️ EM RISCO"},
    "crm_stalled":              {"EN": "🚧 STALLED",             "PT": "🚧 PARADOS"},
    "crm_open_pipeline":        {"EN": "💰 OPEN PIPELINE",       "PT": "💰 PIPELINE ABERTO"},
    "crm_all_stages":           {"EN": "All Stages",             "PT": "Todos os Estágios"},
    "crm_sort_by":              {"EN": "Sort by",                "PT": "Ordenar por"},
    "crm_value_desc":           {"EN": "Value ↓",                "PT": "Valor ↓"},
    "crm_close_date":           {"EN": "Close Date ↑",           "PT": "Data de Fechamento ↑"},
    "crm_risk_first":           {"EN": "Risk First",             "PT": "Risco Primeiro"},
    "crm_filter_stage":         {"EN": "Filter Stage",           "PT": "Filtrar Estágio"},
    "crm_pipeline_by_stage":    {"EN": "### 📊 Pipeline by Stage", "PT": "### 📊 Pipeline por Estágio"},
    "crm_deal_aging":           {"EN": "### ⏱️ Deal Aging (Days Open)", "PT": "### ⏱️ Idade do Negócio (Dias em Aberto)"},
    "crm_expected_close":       {"EN": "### 📅 Expected Close Dates", "PT": "### 📅 Datas de Fechamento Esperadas"},
    "crm_win_loss":             {"EN": "### 🎯 Win/Loss Analysis", "PT": "### 🎯 Análise de Ganhos/Perdas"},

    # ── Outreach ─────────────────────────────────────────────────────────────
    "page_outreach":            {"EN": "📧 Outreach Performance", "PT": "📧 Desempenho de Prospecção"},
    "outreach_caption":         {"EN": "Track email engagement, response rates, and sequence efficiency.", "PT": "Acompanhe engajamento de e-mails, taxas de resposta e eficiência das sequências."},
    "metric_sent":              {"EN": "📤 SENT",                "PT": "📤 ENVIADOS"},
    "metric_opened":            {"EN": "📖 OPENED",              "PT": "📖 ABERTOS"},
    "metric_replied":           {"EN": "💬 REPLIED",             "PT": "💬 RESPONDIDOS"},
    "metric_interested":        {"EN": "🤝 INTERESTED",          "PT": "🤝 INTERESSADOS"},
    "metric_velocity":          {"EN": "⚡ VELOCITY",            "PT": "⚡ VELOCIDADE"},
    "chart_touch_performance":  {"EN": "### 📊 Touch Performance by Sequence",  "PT": "### 📊 Performance por Toque na Sequência"},
    "chart_response_types":     {"EN": "### 💬 Response Types",  "PT": "### 💬 Tipos de Resposta"},
    "chart_weekly_email_trend": {"EN": "### 📈 Weekly Email Trend", "PT": "### 📈 Tendência Semanal de E-mails"},
    "sent_label":               {"EN": "Sent",                   "PT": "Enviados"},
    "opened_label":             {"EN": "Opened",                 "PT": "Abertos"},
    "replied_label":            {"EN": "Replied",                "PT": "Respondidos"},

    # ── Post-Sales ───────────────────────────────────────────────────────────
    "page_postsales":           {"EN": "🏦 Post-Sales & NDR Dashboard", "PT": "🏦 Painel de Pós-Venda & NDR"},
    "post_sales_caption":       {"EN": "Tracking Net Dollar Retention, Account Health, and Upsell Pipeline across the active customer base.", "PT": "Acompanhamento da Retenção Líquida de Receita, Saúde da Conta e Pipeline de Upsell na base de clientes ativos."},
    "post_sales_ndr":           {"EN": "Net Dollar Retention",   "PT": "Retenção Líquida de Receita (NDR)"},
    "post_sales_grr":           {"EN": "Gross Revenue Retention","PT": "Retenção Bruta de Receita (GRR)"},
    "post_sales_renewals":      {"EN": "Active Renewals (90d)",  "PT": "Renovações Ativas (90d)"},
    "post_sales_churn":         {"EN": "Logo Churn Rate",        "PT": "Taxa de Churn de Clientes"},
    "post_sales_waterfall":     {"EN": "### 📈 ARR Composition Waterfall", "PT": "### 📈 Cascata de Composição do ARR"},
    "post_sales_health":        {"EN": "### ❤️ Account Health Scores", "PT": "### ❤️ Pontuações de Saúde das Contas"},
    "post_sales_risk":          {"EN": "Revenue at Critical Risk", "PT": "Receita em Risco Crítico"},
    "metric_ndr":               {"EN": "📈 NET DOLLAR RETENTION", "PT": "📈 RETENÇÃO LÍQUIDA (NDR)"},
    "metric_logo_retention":    {"EN": "🏷️ LOGO RETENTION",     "PT": "🏷️ RETENÇÃO DE CLIENTES"},
    "metric_expansion_rev":     {"EN": "💹 EXPANSION REVENUE",   "PT": "💹 RECEITA DE EXPANSÃO"},
    "metric_churn_rev":         {"EN": "📉 CHURNED REVENUE",     "PT": "📉 RECEITA DE CHURN"},
    "metric_active_accounts":   {"EN": "🏢 ACTIVE ACCOUNTS",     "PT": "🏢 CONTAS ATIVAS"},
    "metric_health_score":      {"EN": "❤️ AVG HEALTH SCORE",   "PT": "❤️ PONTUAÇÃO MÉDIA DE SAÚDE"},
    "section_acct_health":      {"EN": "### ❤️ Account Health Scores", "PT": "### ❤️ Pontuação de Saúde das Contas"},
    "section_risk_accounts":    {"EN": "### 🚨 At-Risk Accounts",  "PT": "### 🚨 Contas em Risco"},

    # ── Generate Leads ───────────────────────────────────────────────────────
    "page_leads":               {"EN": "⚡ Generate Leads",   "PT": "⚡ Gerar Leads"},
    "leads_caption":            {"EN": "Apply filters, discover qualified leads, import into campaigns.",
                                 "PT": "Aplique filtros, descubra leads qualificados e importe para campanhas."},
    "btn_generate":             {"EN": "🚀 Generate Batch",      "PT": "🚀 Gerar Lote"},
    "btn_export_csv":           {"EN": "⬇️ Export CSV",          "PT": "⬇️ Exportar CSV"},
    "btn_import_crm":           {"EN": "💼 Import to CRM",       "PT": "💼 Importar para CRM"},
    "filter_industry":          {"EN": "Industry",               "PT": "Setor"},
    "filter_company_size":      {"EN": "Company Size",           "PT": "Tamanho da Empresa"},
    "filter_country":           {"EN": "Country",                "PT": "País"},
    "filter_min_score":         {"EN": "Min Score",              "PT": "Pontuação Mínima"},
    "filter_all":               {"EN": "All",                    "PT": "Todos"},
    "label_total_leads":        {"EN": "Total Leads",            "PT": "Total de Leads"},
    "label_avg_score":          {"EN": "Avg Score",              "PT": "Pontuação Média"},
    "label_high_priority":      {"EN": "High Priority",          "PT": "Alta Prioridade"},
    "label_enterprise":         {"EN": "Enterprise",             "PT": "Enterprise"},

    # ── AI Copilot ───────────────────────────────────────────────────────────
    "page_copilot":             {"EN": "💬 AI RevOps Copilot", "PT": "💬 Copiloto IA RevOps"},
    "copilot_caption":          {"EN": "Ask anything about your pipeline, quota attainment, or revenue strategy.",
                                 "PT": "Pergunte qualquer coisa sobre pipeline, atingimento de quota ou estratégia de receita."},
    "copilot_welcome":          {"EN": "Welcome to your command center. I am analyzing your real-time data. What would you like to know about our revenue trajectory?", "PT": "Bem-vindo à sua central de comando. Estou analisando seus dados em tempo real. O que você gostaria de saber sobre a trajetória da nossa receita?"},
    "copilot_btn_risk":         {"EN": "📊 Analyze Pipeline Risk", "PT": "📊 Analisar Risco do Pipeline"},
    "copilot_btn_ceo":          {"EN": "👑 CEO: Company Valuation Status", "PT": "👑 CEO: Status do Valuation da Empresa"},
    "copilot_btn_forecast":     {"EN": "🎯 Sales Forecast to Target", "PT": "🎯 Previsão de Vendas vs Meta"},
    "copilot_btn_vpsales":      {"EN": "📈 VP Sales: Rep Performance", "PT": "📈 VP Vendas: Performance dos Representantes"},
    "copilot_btn_summary":      {"EN": "💡 Provide Executive Summary", "PT": "💡 Fornecer Resumo Executivo"},
    "copilot_btn_vprev":        {"EN": "🏦 VP Revenue: Net Retention Forecast", "PT": "🏦 VP Receitas: Previsão de Retenção Líquida"},
    "copilot_input":            {"EN": "Ask about revenue, conversions, or specific reps...", "PT": "Pergunte sobre receita, conversões ou representantes específicos..."},
    "copilot_spinner":          {"EN": "Analyzing RevOps engine...", "PT": "Analisando o motor RevOps..."},
    "copilot_placeholder":      {"EN": "Ask the AI about your pipeline…", "PT": "Pergunte à IA sobre seu pipeline…"},
    "copilot_thinking":         {"EN": "Thinking…",              "PT": "Pensando…"},
    "copilot_you":              {"EN": "You",                    "PT": "Você"},
    "copilot_ai":               {"EN": "AI Copilot",             "PT": "Copiloto IA"},

    # ── Lead Intelligence ────────────────────────────────────────────────────
    "page_intel":               {"EN": "🔍 Lead Intelligence", "PT": "🔍 Inteligência de Leads"},
    "intel_caption":            {"EN": "Deep-dive into any lead profile.",
                                 "PT": "Aprofunde-se no perfil de qualquer lead."},
    "intel_search":             {"EN": "🔍 Search lead by company or contact…",  "PT": "🔍 Buscar lead por empresa ou contato…"},
    "label_enrichment":         {"EN": "🔬 ENRICHMENT DATA",     "PT": "🔬 DADOS DE ENRIQUECIMENTO"},
    "label_deal_brief":         {"EN": "📞 DEAL BRIEF",          "PT": "📞 RESUMO DO NEGÓCIO"},
    "label_outreach_cadence":   {"EN": "📧 OUTREACH CADENCE",    "PT": "📧 CADÊNCIA DE PROSPECÇÃO"},
    "nav_tech_gaps":            {"EN": "**Tech Gaps**",          "PT": "**Gaps Tecnológicos**"},
    "nav_buying_signals":       {"EN": "**Buying Signals**",     "PT": "**Sinais de Compra**"},

    # ── Sales Navigator ──────────────────────────────────────────────────────
    "page_navigator":           {"EN": "🧭 Sales Navigator",  "PT": "🧭 Navegador de Vendas"},
    "nav_caption":              {"EN": "Identify and prioritise top accounts.",
                                 "PT": "Identifique e priorize as principais contas."},
    "nav_btn_email":            {"EN": "📧 Send Email",          "PT": "📧 Enviar E-mail"},
    "nav_btn_wa":               {"EN": "📱 WhatsApp",            "PT": "📱 WhatsApp"},
    "nav_btn_li":               {"EN": "💼 Send LinkedIn",       "PT": "💼 Enviar LinkedIn"},
    "nav_btn_web":              {"EN": "🌐 Company Website",     "PT": "🌐 Site da Empresa"},
    "nav_btn_co_li":            {"EN": "🔗 Company LinkedIn",    "PT": "🔗 LinkedIn da Empresa"},

    # ── Footer ───────────────────────────────────────────────────────────────
    "footer":                   {"EN": "LeadEngine v3.0 · **B2B Autonomous Lead Engine** - RexOps Command Center",
                                 "PT": "LeadEngine v3.0 · **Motor Autônomo de Leads B2B** - Central de Comando RevOps"},
}


def get_lang() -> str:
    """Return the active language code from session state."""
    import streamlit as st  # local import to avoid circular deps
    return st.session_state.get("lang", "EN")


def t(key: str, **kwargs) -> str:
    """
    Return the translation for `key` in the active language.
    Falls back to English if the key or language is missing.
    Supports simple format kwargs, e.g. t("quota_of_target", target="$500K").
    """
    lang = get_lang()
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get("EN", f"[{key}]")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
