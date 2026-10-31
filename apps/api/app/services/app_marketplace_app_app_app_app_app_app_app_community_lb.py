"""Community leaderboard — rank community contributors by engagement."""
from __future__ import annotations


def build_community_leaderboard(members: list[dict], *, period: str = "monthly") -> dict:
    scored = []
    for m in members:
        score = (m.get("forum_posts", 0) * 2 + m.get("forum_replies", 0) * 1 +
                 m.get("bugs_reported", 0) * 5 + m.get("apps_published", 0) * 20 +
                 m.get("reviews_written", 0) * 3)
        scored.append({**m, "score": score})
    scored.sort(key=lambda x: -x["score"])
    for i, s in enumerate(scored):
        s["rank"] = i + 1
        s["badge"] = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
    return {"leaderboard": scored, "period": period, "total": len(scored),
            "top_contributor": scored[0]["name"] if scored else None}
