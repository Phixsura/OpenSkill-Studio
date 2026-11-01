"""Pricing tier selector — help users choose the right plan."""


TIERS = [
    {"id": "free", "name": "Free", "price": 0, "billing": "forever",
     "features": ["5 apps", "1K API calls/mo", "Community support"],
     "highlighted": False, "cta": "Get Started"},
    {"id": "starter", "name": "Starter", "price": 29, "billing": "/month",
     "features": ["25 apps", "50K API calls/mo", "Email support", "Analytics"],
     "highlighted": False, "cta": "Start Free Trial"},
    {"id": "pro", "name": "Pro", "price": 99, "billing": "/month",
     "features": ["Unlimited apps", "500K API calls/mo", "Priority support", "Analytics", "Custom domain", "Webhooks"],
     "highlighted": True, "cta": "Start Free Trial"},
    {"id": "enterprise", "name": "Enterprise", "price": -1, "billing": "custom",
     "features": ["Everything in Pro", "Unlimited API calls", "SLA", "SSO", "Dedicated support", "Custom contracts"],
     "highlighted": False, "cta": "Contact Sales"},
]


def get_pricing_tiers(*, annual_discount_pct: float = 20) -> dict:
    tiers = []
    for t in TIERS:
        annual_price = round(t["price"] * 12 * (1 - annual_discount_pct / 100)) if t["price"] > 0 else 0
        tiers.append({**t, "annual_price": annual_price,
                      "annual_monthly": round(annual_price / 12, 2) if annual_price > 0 else 0})
    return {"tiers": tiers, "annual_discount_pct": annual_discount_pct}


def recommend_tier(*, usage: dict) -> dict:
    apps = usage.get("apps", 0)
    api_calls = usage.get("api_calls_monthly", 0)
    if apps <= 5 and api_calls <= 1000:
        return {"recommended": "free", "reason": "Your usage fits the free tier"}
    if apps <= 25 and api_calls <= 50000:
        return {"recommended": "starter", "reason": "Best value for your current usage"}
    if api_calls <= 500000:
        return {"recommended": "pro", "reason": "Unlock unlimited apps and advanced features"}
    return {"recommended": "enterprise", "reason": "Custom solution for your scale"}
