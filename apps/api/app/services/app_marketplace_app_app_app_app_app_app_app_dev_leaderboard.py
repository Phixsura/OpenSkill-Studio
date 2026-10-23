"""Developer activity leaderboard — rank developers by contributions."""
from __future__ import annotations


def build_leaderboard(developers: list[dict], *, period: str = "monthly") -> dict:
    scored = []
    for d in developers:
        commits = d.get("commits", 0)
        prs = d.get("pull_requests", 0)
        reviews = d.get("reviews", 0)
        deploys = d.get("deploys", 0)
        score = commits * 1 + prs * 5 + reviews * 3 + deploys * 10
        scored.append({
            "name": d["name"], "avatar": d.get("avatar", ""),
            "commits": commits, "pull_requests": prs,
            "reviews": reviews, "deploys": deploys,
            "score": score,
        })
    scored.sort(key=lambda x: -x["score"])
    for i, d in enumerate(scored):
        d["rank"] = i + 1
        d["badge"] = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
    return {"leaderboard": scored, "period": period,
            "total_developers": len(scored),
            "top_contributor": scored[0]["name"] if scored else None}
