"""
B2B Lead Engine — Sample Data Generator (Expanded)

Creates 150 realistic mock companies and 200+ contacts for demo/testing.
Includes US, Brazil, and international markets.
"""

from __future__ import annotations

import random
from hashlib import md5

from src.models.models import Company, Contact


# ── Company Name Components ───────────────────────────

PREFIXES = [
    "Nova", "Apex", "Cloud", "Data", "Rev", "Growth", "Pixel", "Sync",
    "Pulse", "Forge", "Stack", "Velo", "Flux", "Orbit", "Prism", "Vertex",
    "Neo", "Quantum", "Atlas", "Helix", "Onyx", "Ember", "Zeta", "Arc",
    "Core", "Drift", "Echo", "Fuse", "Glyph", "Hive", "Ion", "Kite",
    "Lyra", "Mint", "Nexus", "Opal", "Peak", "Raze", "Sage", "Tide",
    "Uno", "Volt", "Warp", "Xeno", "Yara", "Zinc", "Bolt", "Crest",
]

SUFFIXES_US = [
    "Tech", "Systems", "AI", "Labs", "Cloud", "Analytics", "Software",
    "Solutions", "HQ", "Digital", "Dynamics", "Pro", "Logic", "Works",
    "Stream", "Ware", "Hub", "Bridge", "Point", "Scale",
]

SUFFIXES_BR = [
    "Tech", "Soluções", "Digital", "Sistemas", "Inovação",
    "Dados", "Software", "Labs", "Tecnologia", "Brasil",
]

SUFFIXES_INTL = [
    "Global", "International", "Technologies", "Corp", "Group",
    "Ventures", "Partners", "Networks", "Platforms", "Services",
]

# ── Industries ────────────────────────────────────────

US_INDUSTRIES = [
    "B2B SaaS", "Enterprise Software", "Cloud Infrastructure",
    "Data Analytics", "MarTech", "RevOps / Sales Tech", "FinTech",
    "HealthTech", "EdTech", "Cybersecurity", "AI/ML Platform",
    "DevOps Tools", "HR Tech", "Legal Tech", "PropTech",
]

BR_INDUSTRIES = [
    "Tecnologia da Informação", "Software", "E-commerce", "FinTech",
    "AgriTech", "HealthTech", "EdTech", "Logística", "RetailTech",
]

INTL_INDUSTRIES = [
    "Enterprise Software", "Cloud Infrastructure", "FinTech",
    "Data Analytics", "Cybersecurity", "AI/ML Platform",
]

# ── Geography ─────────────────────────────────────────

US_STATES = ["CA", "NY", "TX", "MA", "WA", "CO", "IL", "FL", "GA", "NC", "PA", "OH", "AZ", "UT", "OR"]
BR_STATES = ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "PE", "CE", "DF"]
INTL_COUNTRIES = [
    ("UK", "London"), ("DE", "Berlin"), ("FR", "Paris"),
    ("IL", "Tel Aviv"), ("SG", "Singapore"), ("AU", "Sydney"),
    ("CA", "Toronto"), ("NL", "Amsterdam"), ("SE", "Stockholm"),
    ("IN", "Bangalore"), ("JP", "Tokyo"), ("KR", "Seoul"),
]

# ── Tech Stacks ───────────────────────────────────────

TECH_STACKS_POOL = {
    "no_crm": [
        ["Google Sheets", "Mailchimp"],
        ["Excel", "Outlook"],
        ["Google Sheets", "Zapier"],
        ["Airtable", "Mailchimp"],
        ["Notion", "Manual Tracking"],
        ["Planilhas", "RD Station"],
    ],
    "basic_crm": [
        ["Pipedrive", "Google Analytics"],
        ["HubSpot Free", "Mailchimp"],
        ["Zoho CRM", "Google Analytics"],
        ["Freshsales", "SendGrid"],
    ],
    "enterprise": [
        ["Salesforce", "Marketo", "Tableau"],
        ["Salesforce", "Pardot", "Power BI"],
        ["SAP", "Oracle", "Jira"],
        ["HubSpot Enterprise", "Segment", "Amplitude"],
        ["Salesforce", "Snowflake", "dbt", "Looker"],
    ],
    "modern_stack": [
        ["HubSpot", "Mixpanel", "Segment"],
        ["Pipedrive", "Intercom", "Amplitude"],
        ["Close.io", "Customer.io", "Metabase"],
        ["Apollo", "Outreach", "Gong"],
    ],
}

FUNDING_STAGES = [
    "Pre-Seed", "Seed", "Series A", "Series B", "Series C",
    "Series D", "Growth", "Bootstrapped", "Public",
]

FUNDING_WEIGHTS = [5, 15, 25, 20, 12, 5, 3, 12, 3]  # realistic distribution

# ── Contact Templates ─────────────────────────────────

PERSONA_TEMPLATES_US = [
    {"title": "VP of Sales", "seniority": "VP", "department": "Sales"},
    {"title": "Head of Revenue Operations", "seniority": "Director", "department": "Revenue Operations"},
    {"title": "CRO", "seniority": "C-Level", "department": "Revenue"},
    {"title": "VP of Marketing", "seniority": "VP", "department": "Marketing"},
    {"title": "Head of Growth", "seniority": "Director", "department": "Growth"},
    {"title": "SDR Manager", "seniority": "Manager", "department": "Sales"},
    {"title": "Director of Sales", "seniority": "Director", "department": "Sales"},
    {"title": "CMO", "seniority": "C-Level", "department": "Marketing"},
    {"title": "Sales Operations Manager", "seniority": "Manager", "department": "Sales Operations"},
    {"title": "VP of Business Development", "seniority": "VP", "department": "Business Development"},
    {"title": "Account Executive", "seniority": "Individual Contributor", "department": "Sales"},
    {"title": "Revenue Analyst", "seniority": "Individual Contributor", "department": "Revenue Operations"},
]

PERSONA_TEMPLATES_BR = [
    {"title": "Diretor Comercial", "seniority": "Director", "department": "Comercial"},
    {"title": "Head de Vendas", "seniority": "Director", "department": "Vendas"},
    {"title": "VP de Receita", "seniority": "VP", "department": "Revenue"},
    {"title": "Gerente de Operações de Vendas", "seniority": "Manager", "department": "Sales Operations"},
    {"title": "Coordenador de Marketing", "seniority": "Manager", "department": "Marketing"},
    {"title": "Analista de RevOps", "seniority": "Individual Contributor", "department": "Revenue Operations"},
]

FIRST_NAMES = [
    "Sarah", "Michael", "Emily", "James", "Ana", "Carlos", "Maria",
    "David", "Jennifer", "Roberto", "Lucas", "Fernanda", "Rafael", "Jessica",
    "Alex", "Jordan", "Taylor", "Camila", "Gabriel", "Sophia",
    "Daniel", "Olivia", "Mateus", "Isabella", "Ethan", "Mia", "Liam",
    "Noah", "Emma", "Ava", "William", "Charlotte", "Benjamin", "Amelia",
    "Hiroshi", "Yuki", "Wei", "Priya", "Raj", "Aisha", "Omar",
    "Sofia", "Diego", "Valentina", "André", "Beatriz", "Thiago", "Juliana",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Davis", "Silva", "Santos",
    "Oliveira", "Souza", "Chen", "Kim", "Patel", "Garcia", "Martinez",
    "Anderson", "Taylor", "Thomas", "Ferreira", "Costa", "Rodrigues",
    "Wilson", "Moore", "Jackson", "White", "Harris", "Clark", "Lewis",
    "Lee", "Walker", "Hall", "Allen", "Young", "Wright", "King",
    "Tanaka", "Wang", "Müller", "Johansson", "Van der Berg", "O'Brien",
    "Almeida", "Nascimento", "Carvalho", "Lima", "Mendes", "Ribeiro",
]

# ── Data Sources ──────────────────────────────────────

US_SOURCES = ["apollo", "crunchbase", "sec_edgar", "linkedin", "opencorporates"]
BR_SOURCES = ["receita_federal", "dados_abertos", "apollo", "linkedin"]
INTL_SOURCES = ["apollo", "crunchbase", "opencorporates", "linkedin"]


def _deterministic_seed(name: str) -> int:
    """Create a deterministic seed from a string for reproducible randomness."""
    return int(md5(name.encode()).hexdigest()[:8], 16)


def _generate_company_name(prefix: str, suffix: str) -> str:
    return f"{prefix}{suffix}"


def _generate_revenue(funding_stage: str) -> float:
    """Generate realistic revenue based on funding stage."""
    ranges = {
        "Pre-Seed": (100_000, 500_000),
        "Seed": (300_000, 3_000_000),
        "Series A": (2_000_000, 15_000_000),
        "Series B": (8_000_000, 50_000_000),
        "Series C": (25_000_000, 150_000_000),
        "Series D": (50_000_000, 300_000_000),
        "Growth": (100_000_000, 500_000_000),
        "Bootstrapped": (500_000, 20_000_000),
        "Public": (200_000_000, 2_000_000_000),
    }
    lo, hi = ranges.get(funding_stage, (1_000_000, 10_000_000))
    return round(random.uniform(lo, hi), -3)  # round to nearest 1K


def _generate_headcount(revenue: float) -> int:
    """Generate realistic headcount based on revenue."""
    ratio = random.uniform(80_000, 200_000)  # revenue per employee range
    base = max(10, int(revenue / ratio))
    return min(5000, base + random.randint(-5, 20))


def _generate_website(name: str, country: str) -> str:
    slug = name.lower().replace(" ", "").replace("/", "")
    tld = ".com.br" if country == "BR" else ".io" if random.random() > 0.5 else ".com"
    return f"https://{slug}{tld}"


def _generate_cnpj() -> str:
    parts = [
        f"{random.randint(10, 99)}",
        f"{random.randint(100, 999)}",
        f"{random.randint(100, 999)}",
        f"0001",
        f"{random.randint(10, 99)}",
    ]
    return f"{parts[0]}.{parts[1]}.{parts[2]}/{parts[3]}-{parts[4]}"


def generate_seed_companies() -> list[Company]:
    """Generate 150 realistic seed companies (100 US, 35 BR, 15 intl)."""
    random.seed(42)  # reproducible
    companies = []
    used_names = set()

    def _unique_name(prefix_pool, suffix_pool):
        for _ in range(100):
            p = random.choice(prefix_pool)
            s = random.choice(suffix_pool)
            name = f"{p}{s}"
            if name not in used_names:
                used_names.add(name)
                return name
        return f"Company{len(used_names)}"

    # ── 100 US Companies ──────────────────────────────
    for i in range(100):
        funding = random.choices(FUNDING_STAGES, weights=FUNDING_WEIGHTS, k=1)[0]
        revenue = _generate_revenue(funding)
        headcount = _generate_headcount(revenue)
        name = _unique_name(PREFIXES, SUFFIXES_US)

        # Deterministic tech stack category based on company
        r = random.random()
        if r < 0.35:
            tech = random.choice(TECH_STACKS_POOL["no_crm"])
        elif r < 0.55:
            tech = random.choice(TECH_STACKS_POOL["basic_crm"])
        elif r < 0.75:
            tech = random.choice(TECH_STACKS_POOL["modern_stack"])
        else:
            tech = random.choice(TECH_STACKS_POOL["enterprise"])

        companies.append(Company(
            name=name,
            industry=random.choice(US_INDUSTRIES),
            country="US",
            state=random.choice(US_STATES),
            employee_count=headcount,
            revenue_usd=revenue,
            website=_generate_website(name, "US"),
            tech_stack=tech,
            funding_stage=funding,
            founded_year=random.randint(2010, 2024),
            source=random.choice(US_SOURCES),
        ))

    # ── 35 Brazil Companies ───────────────────────────
    BR_CNAE_CODES = ["6201-5", "6202-3", "6203-1", "6204-0", "6311-9", "6319-4", "6399-2"]

    for i in range(35):
        funding = random.choices(FUNDING_STAGES, weights=FUNDING_WEIGHTS, k=1)[0]
        revenue = _generate_revenue(funding)
        headcount = _generate_headcount(revenue)
        name = _unique_name(PREFIXES, SUFFIXES_BR)

        r = random.random()
        if r < 0.40:
            tech = random.choice(TECH_STACKS_POOL["no_crm"])
        elif r < 0.65:
            tech = random.choice(TECH_STACKS_POOL["basic_crm"])
        elif r < 0.80:
            tech = random.choice(TECH_STACKS_POOL["modern_stack"])
        else:
            tech = random.choice(TECH_STACKS_POOL["enterprise"])

        companies.append(Company(
            name=name,
            industry=random.choice(BR_INDUSTRIES),
            country="BR",
            state=random.choice(BR_STATES),
            employee_count=headcount,
            revenue_usd=revenue,
            website=_generate_website(name, "BR"),
            tech_stack=tech,
            funding_stage=funding,
            founded_year=random.randint(2012, 2024),
            cnpj=_generate_cnpj(),
            cnae_code=random.choice(BR_CNAE_CODES),
            source=random.choice(BR_SOURCES),
        ))

    # ── 15 International Companies ────────────────────
    for i in range(15):
        funding = random.choices(FUNDING_STAGES, weights=FUNDING_WEIGHTS, k=1)[0]
        revenue = _generate_revenue(funding)
        headcount = _generate_headcount(revenue)
        name = _unique_name(PREFIXES, SUFFIXES_INTL)
        country_data = random.choice(INTL_COUNTRIES)

        r = random.random()
        if r < 0.30:
            tech = random.choice(TECH_STACKS_POOL["no_crm"])
        elif r < 0.50:
            tech = random.choice(TECH_STACKS_POOL["basic_crm"])
        elif r < 0.75:
            tech = random.choice(TECH_STACKS_POOL["modern_stack"])
        else:
            tech = random.choice(TECH_STACKS_POOL["enterprise"])

        companies.append(Company(
            name=name,
            industry=random.choice(INTL_INDUSTRIES),
            country=country_data[0],
            state=country_data[1],
            employee_count=headcount,
            revenue_usd=revenue,
            website=_generate_website(name, country_data[0]),
            tech_stack=tech,
            funding_stage=funding,
            founded_year=random.randint(2010, 2024),
            source=random.choice(INTL_SOURCES),
        ))

    return companies


def generate_seed_contacts(companies: list[Company]) -> list[Contact]:
    """Generate 1-3 contacts per company (~250+ total)."""
    random.seed(43)  # reproducible but different from companies
    contacts = []

    for company in companies:
        # More contacts for larger companies
        if company.employee_count > 200:
            num_contacts = random.randint(2, 3)
        elif company.employee_count > 50:
            num_contacts = random.randint(1, 3)
        else:
            num_contacts = random.randint(1, 2)

        # Select persona templates based on market
        if company.country == "BR":
            personas = random.sample(
                PERSONA_TEMPLATES_BR,
                min(num_contacts, len(PERSONA_TEMPLATES_BR)),
            )
        else:
            personas = random.sample(
                PERSONA_TEMPLATES_US,
                min(num_contacts, len(PERSONA_TEMPLATES_US)),
            )

        for tmpl in personas:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            domain = company.website.replace("https://", "").replace("http://", "")

            contacts.append(
                Contact(
                    company_id=company.company_id,
                    full_name=f"{first} {last}",
                    title=tmpl["title"],
                    email=f"{first.lower()}.{last.lower()}@{domain}",
                    phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    linkedin_url=f"linkedin.com/in/{first.lower()}{last.lower()}{random.randint(1, 999)}",
                    seniority=tmpl["seniority"],
                    department=tmpl["department"],
                    source=random.choice(["apollo", "hunter", "linkedin", "manual"]),
                    verified=random.random() > 0.25,
                )
            )

    return contacts
