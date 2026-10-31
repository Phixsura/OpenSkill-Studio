"""Trust badges — display trust signals for marketplace apps."""
from __future__ import annotations

BADGES = {
    "verified": {"icon": "✅", "label": "Verified Developer", "color": "blue"},
    "security_reviewed": {"icon": "🔒", "label": "Security Reviewed", "color": "green"},
    "soc2": {"icon": "🛡️", "label": "SOC2 Compliant", "color": "purple"},
    "gdpr": {"icon": "🇪🇺", "label": "GDPR Compliant", "color": "blue"},
    "partner": {"icon": "🤝", "label": "Official Partner", "color": "gold"},
    "top_rated": {"icon": "⭐", "label": "Top Rated", "color": "yellow"},
    "fast_support": {"icon": "⚡", "label": "Fast Support", "color": "green"},
}


def get_badges(badge_ids: list[str]) -> list[dict]:
    return [{"id": bid, **BADGES[bid]} for bid in badge_ids if bid in BADGES]


def compute_trust_score(badges: list[str]) -> dict:
    score = len([b for b in badges if b in BADGES]) * 15
    score = min(100, score)
    level = "high" if score >= 60 else "medium" if score >= 30 else "low"
    return {"score": score, "level": level, "badge_count": len(badges)}
