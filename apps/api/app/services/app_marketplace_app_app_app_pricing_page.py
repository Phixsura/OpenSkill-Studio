"""App pricing page — complete pricing page with FAQ."""

import html

PRICING_TIERS = [
    {"id": "free", "name": "Free", "price": 0, "interval": "forever", "recommended": False,
     "features": ["5 apps", "1K API calls/mo", "Community support", "Basic analytics"]},
    {"id": "pro", "name": "Pro", "price": 29, "interval": "month", "recommended": True,
     "features": ["Unlimited apps", "500K API calls/mo", "Priority support", "Advanced analytics",
                   "Custom domain", "Webhooks", "Team collaboration"]},
    {"id": "enterprise", "name": "Enterprise", "price": -1, "interval": "custom", "recommended": False,
     "features": ["Everything in Pro", "Unlimited API calls", "Dedicated support", "SLA",
                   "SSO/SAML", "Audit logs", "Custom integrations", "On-premise option"]},
]

FAQ = [
    {"q": "Can I switch plans anytime?", "a": "Yes, upgrade or downgrade anytime. Changes take effect immediately."},
    {"q": "What happens when I exceed my limits?", "a": "We'll notify you and offer to upgrade. Your app continues working."},
    {"q": "Is there a free trial for Pro?", "a": "Yes, Pro includes a 14-day free trial. No credit card required."},
]


def build_pricing_page() -> dict:
    tiers = []
    for t in PRICING_TIERS:
        price_display = "Free" if t["price"] == 0 else "Custom" if t["price"] < 0 else f"${t['price']}/mo"
        tiers.append({**t, "price_display": price_display, "feature_count": len(t["features"])})
    return {"tiers": tiers, "faq": FAQ, "tier_count": len(tiers), "faq_count": len(FAQ)}
