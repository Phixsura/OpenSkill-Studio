"""Developer program tiers — manage developer program membership levels."""
from __future__ import annotations

TIERS = {
    "community": {"label": "Community", "icon": "🌱", "fee": 0, "benefits": [
        "Marketplace listing", "Community support", "Basic analytics"]},
    "verified": {"label": "Verified", "icon": "✅", "fee": 0, "benefits": [
        "Verified badge", "Priority support", "Advanced analytics", "Featured placement"]},
    "partner": {"label": "Partner", "icon": "🤝", "fee": 99, "benefits": [
        "Partner badge", "Dedicated support", "Revenue sharing", "Co-marketing",
        "Early API access", "Custom integrations"]},
    "premier": {"label": "Premier", "icon": "💎", "fee": 499, "benefits": [
        "Premier badge", "Account manager", "SLA", "Custom contracts",
        "Private beta access", "Joint roadmap planning", "Logo placement"]},
}


def get_tier(tier_id: str) -> dict | None:
    t = TIERS.get(tier_id)
    return {"id": tier_id, **t, "benefit_count": len(t["benefits"]),
            "fee_display": "Free" if t["fee"] == 0 else f"${t['fee']}/mo"} if t else None


def compare_tiers() -> list[dict]:
    all_benefits = sorted({b for t in TIERS.values() for b in t["benefits"]})
    return [{"id": k, "label": v["label"], "icon": v["icon"],
             "fee_display": "Free" if v["fee"] == 0 else f"${v['fee']}/mo",
             "benefits": {b: b in v["benefits"] for b in all_benefits}}
            for k, v in TIERS.items()]


def recommend_tier(*, app_count: int, installs: int, revenue: float) -> str:
    if revenue > 10000 or installs > 500000:
        return "premier"
    if revenue > 1000 or installs > 50000:
        return "partner"
    if app_count >= 3:
        return "verified"
    return "community"
