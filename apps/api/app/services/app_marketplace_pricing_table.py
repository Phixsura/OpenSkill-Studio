"""Pricing table — build comparison pricing table for app plans."""

PLAN_FEATURES = {
    "free": {"price_cents": 0, "label": "Free", "features": ["1 app", "1K API calls/day", "Community support", "Basic analytics"],
             "cta": "Get Started", "highlighted": False},
    "starter": {"price_cents": 2900, "label": "Starter", "features": ["5 apps", "50K API calls/day", "Email support",
                "Full analytics", "Custom webhooks", "Team (5 members)"], "cta": "Start Free Trial", "highlighted": False},
    "pro": {"price_cents": 9900, "label": "Pro", "features": ["25 apps", "500K API calls/day", "Priority support",
            "Advanced analytics", "Custom domains", "Team (20 members)", "SSO", "SLA 99.9%"],
            "cta": "Start Free Trial", "highlighted": True},
    "enterprise": {"price_cents": -1, "label": "Enterprise", "features": ["Unlimited apps", "Unlimited API calls",
                   "Dedicated support", "Custom analytics", "Multi-region", "Unlimited team", "SSO + SAML",
                   "SLA 99.99%", "Custom contracts"], "cta": "Contact Sales", "highlighted": False},
}


def get_pricing_table() -> list[dict]:
    return [{"id": k, **v} for k, v in PLAN_FEATURES.items()]


def get_plan_recommendation(*, usage: dict) -> dict:
    api_calls = usage.get("api_calls_per_day", 0)
    apps = usage.get("app_count", 0)
    team = usage.get("team_size", 0)
    if api_calls <= 1000 and apps <= 1 and team <= 1:
        return {"plan": "free", "reason": "Usage fits within free tier"}
    if api_calls <= 50000 and apps <= 5:
        return {"plan": "starter", "reason": "Growing usage needs Starter features"}
    if api_calls <= 500000 and apps <= 25:
        return {"plan": "pro", "reason": "Professional usage with advanced features"}
    return {"plan": "enterprise", "reason": "High-scale usage needs custom solutions"}


def compute_annual_savings(*, monthly_price: int) -> dict:
    annual_monthly = monthly_price * 12
    annual_price = int(monthly_price * 10)  # 2 months free
    savings = annual_monthly - annual_price
    return {"monthly": monthly_price, "annual_monthly": annual_price // 12,
            "annual_total": annual_price, "savings_cents": savings,
            "savings_pct": round(savings / max(annual_monthly, 1) * 100)}
