"""Pricing page — platform pricing with plan comparison and FAQ."""

PLANS = [
    {"id": "free", "name": "Free", "price_monthly": 0, "price_yearly": 0, "highlighted": False,
     "features": ["1 app", "1,000 API calls/day", "Community support", "Basic analytics"],
     "cta": "Get Started"},
    {"id": "starter", "name": "Starter", "price_monthly": 2900, "price_yearly": 29000, "highlighted": False,
     "features": ["5 apps", "50K API calls/day", "Email support", "Full analytics", "Webhooks", "Team (5)"],
     "cta": "Start Free Trial"},
    {"id": "pro", "name": "Pro", "price_monthly": 9900, "price_yearly": 99000, "highlighted": True,
     "features": ["25 apps", "500K API calls/day", "Priority support", "Advanced analytics",
                   "Custom domains", "Team (20)", "SSO", "SLA 99.9%"],
     "cta": "Start Free Trial"},
    {"id": "enterprise", "name": "Enterprise", "price_monthly": -1, "price_yearly": -1, "highlighted": False,
     "features": ["Unlimited apps", "Unlimited API calls", "Dedicated support", "Custom analytics",
                   "Multi-region", "Unlimited team", "SSO + SAML", "SLA 99.99%", "Custom contracts"],
     "cta": "Contact Sales"},
]

FAQ = [
    {"q": "Can I switch plans?", "a": "Yes, upgrade or downgrade anytime. Changes take effect immediately."},
    {"q": "Is there a free trial?", "a": "Yes, Starter and Pro plans include a 14-day free trial."},
    {"q": "What payment methods?", "a": "We accept all major credit cards, bank transfers, and invoicing for Enterprise."},
    {"q": "Can I cancel anytime?", "a": "Yes, cancel anytime with no penalties. Your data is retained for 30 days."},
]


def build_pricing_page(*, current_plan: str | None = None, annual: bool = False) -> dict:
    plans = []
    for p in PLANS:
        price = p["price_yearly"] // 12 if annual and p["price_yearly"] > 0 else p["price_monthly"]
        plans.append({**p, "display_price": price, "is_current": p["id"] == current_plan,
                        "savings_pct": 17 if annual and p["price_monthly"] > 0 else 0})
    return {"page_type": "pricing", "plans": plans, "annual": annual, "faq": FAQ,
            "trial_days": 14, "money_back_days": 30}
