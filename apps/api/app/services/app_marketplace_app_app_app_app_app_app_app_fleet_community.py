"""Fleet community health — track open source community metrics."""
from __future__ import annotations
def fleet_community_health(metrics: dict) -> dict:
    stars = metrics.get("stars", 0)
    forks = metrics.get("forks", 0)
    contributors = metrics.get("contributors", 0)
    issues_closed_pct = metrics.get("issues_closed_pct", 0)
    score = round((min(stars / 100, 100) + min(contributors * 2, 100) + issues_closed_pct) / 3, 1)
    return {"stars": stars, "forks": forks, "contributors": contributors,
            "score": score, "vibrant": score >= 60}
