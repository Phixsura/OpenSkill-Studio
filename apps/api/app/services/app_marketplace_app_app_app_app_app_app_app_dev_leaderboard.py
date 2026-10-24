"""Developer leaderboard — rank developers by contributions."""
from __future__ import annotations


def build_leaderboard(contributions: list[dict]) -> dict:
    by_dev: dict[str, dict] = {}
    for c in contributions:
        dev = c.get("developer", "")
        if dev not in by_dev:
            by_dev[dev] = {"developer": dev, "commits": 0, "prs": 0, "reviews": 0, "score": 0}
        entry = by_dev[dev]
        entry["commits"] += c.get("commits", 0)
        entry["prs"] += c.get("prs", 0)
        entry["reviews"] += c.get("reviews", 0)
        entry["score"] = entry["commits"] * 1 + entry["prs"] * 5 + entry["reviews"] * 3
    ranked = sorted(by_dev.values(), key=lambda d: -d["score"])
    for i, dev in enumerate(ranked):
        dev["rank"] = i + 1
    return {"leaderboard": ranked, "total_developers": len(ranked),
            "total_commits": sum(d["commits"] for d in ranked)}
