"""Marketplace badges — award badges to apps based on achievements."""

BADGE_DEFINITIONS = {
    "popular": {"icon": "🔥", "label": "Popular", "condition": "100+ installs"},
    "verified_dev": {"icon": "✓", "label": "Verified Developer", "condition": "Developer verified"},
    "high_quality": {"icon": "⭐", "label": "High Quality", "condition": "Health score 95+"},
    "fast": {"icon": "⚡", "label": "Fast", "condition": "Avg latency < 100ms"},
    "new": {"icon": "🆕", "label": "New", "condition": "Published < 30 days ago"},
}


def compute_badges(*, install_count: int, health_score: int, avg_latency_ms: int,
                    developer_verified: bool, days_since_publish: int) -> list[dict]:
    badges = []
    if install_count >= 100:
        badges.append(BADGE_DEFINITIONS["popular"])
    if developer_verified:
        badges.append(BADGE_DEFINITIONS["verified_dev"])
    if health_score >= 95:
        badges.append(BADGE_DEFINITIONS["high_quality"])
    if avg_latency_ms < 100:
        badges.append(BADGE_DEFINITIONS["fast"])
    if days_since_publish <= 30:
        badges.append(BADGE_DEFINITIONS["new"])
    return badges
