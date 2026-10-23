"""Enterprise page — custom enterprise solutions for large organizations."""


def build_enterprise_page(*, features: list[dict] | None = None, case_studies: list[dict] | None = None) -> dict:
    default_features = [
        {"title": "Unlimited Apps", "description": "No limits on apps, API calls, or team members", "icon": "♾️"},
        {"title": "Dedicated Support", "description": "24/7 priority support with dedicated account manager", "icon": "🎯"},
        {"title": "Custom SLA", "description": "99.99% uptime guarantee with custom SLA terms", "icon": "📋"},
        {"title": "SSO & SAML", "description": "Enterprise SSO with SAML, OIDC, and Active Directory", "icon": "🔐"},
        {"title": "Multi-Region", "description": "Deploy across multiple regions for low latency", "icon": "🌍"},
        {"title": "Compliance", "description": "SOC2 Type II, GDPR, HIPAA compliance support", "icon": "✅"},
        {"title": "Custom Contracts", "description": "Flexible billing with annual contracts and invoicing", "icon": "📄"},
        {"title": "Private Marketplace", "description": "Internal marketplace for your organization's apps", "icon": "🏢"},
    ]
    default_case_studies = [
        {"company": "Acme Corp", "industry": "FinTech", "quote": "OpenSkill reduced our integration time by 80%",
         "results": "150+ internal apps, 10K users"},
        {"company": "TechStart", "industry": "SaaS", "quote": "The developer platform transformed how we build",
         "results": "50+ marketplace apps, $2M revenue"},
    ]
    return {
        "page_type": "enterprise",
        "hero": {"title": "OpenSkill for Enterprise", "subtitle": "Scale your platform with enterprise-grade features"},
        "features": features or default_features,
        "case_studies": case_studies or default_case_studies,
        "cta": {"label": "Contact Sales", "url": "/contact?subject=Enterprise"},
        "comparison": {"vs_free": "Everything in Pro, plus:", "extras": ["Unlimited everything", "Custom SLA", "SAML SSO", "Dedicated support"]},
    }
