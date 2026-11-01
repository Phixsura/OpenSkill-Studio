"""User segment — classify users into behavioral segments."""

from datetime import datetime, timedelta


def classify_user(*, user: dict) -> dict:
    segments = []
    installs = user.get("install_count", 0)
    days_active = user.get("days_since_signup", 0)
    reviews = user.get("review_count", 0)
    spend = user.get("total_spend", 0.0)

    if days_active <= 7:
        segments.append("new_user")
    elif days_active <= 30:
        segments.append("onboarding")
    else:
        segments.append("established")

    if installs >= 10:
        segments.append("power_user")
    elif installs >= 3:
        segments.append("active_user")

    if reviews >= 5:
        segments.append("contributor")

    if spend >= 100:
        segments.append("premium")
    elif spend > 0:
        segments.append("paying")

    if user.get("is_developer", False):
        segments.append("developer")

    primary = segments[0] if segments else "unknown"
    return {"user_id": user.get("id", ""), "segments": segments,
            "primary_segment": primary, "segment_count": len(segments)}


def build_segment_summary(*, users: list[dict]) -> dict:
    segment_counts: dict[str, int] = {}
    for u in users:
        result = classify_user(user=u)
        for seg in result["segments"]:
            segment_counts[seg] = segment_counts.get(seg, 0) + 1
    sorted_segs = sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)
    return {"total_users": len(users),
            "segments": [{"name": k, "count": v, "pct": round(v / max(len(users), 1) * 100, 1)} for k, v in sorted_segs]}
