"""Marketplace analytics v2 — platform-wide analytics for marketplace operators."""

from collections import defaultdict


def compute_marketplace_kpis(*, apps: list[dict], installs: list[dict], reviews: list[dict]) -> dict:
    total_apps = len(apps)
    published = sum(1 for a in apps if a.get("status") == "published")
    total_installs = len(installs)
    active_installs = sum(1 for i in installs if i.get("status") == "active")
    avg_rating = round(sum(r.get("rating", 0) for r in reviews) / max(len(reviews), 1), 2)
    return {
        "total_apps": total_apps, "published_apps": published,
        "total_installs": total_installs, "active_installs": active_installs,
        "churn_rate": round((total_installs - active_installs) / max(total_installs, 1) * 100, 1),
        "total_reviews": len(reviews), "avg_rating": avg_rating,
    }


def compute_category_breakdown(*, apps: list[dict]) -> list[dict]:
    cats = defaultdict(lambda: {"count": 0, "installs": 0})
    for a in apps:
        cat = a.get("category", "other")
        cats[cat]["count"] += 1
        cats[cat]["installs"] += a.get("install_count", 0)
    return [{"category": c, **d} for c, d in sorted(cats.items(), key=lambda x: -x[1]["installs"])]


def identify_growth_opportunities(*, kpis: dict) -> list[str]:
    tips = []
    if kpis.get("published_apps", 0) < kpis.get("total_apps", 0) * 0.5:
        tips.append("Many apps are unpublished — consider developer outreach")
    if kpis.get("churn_rate", 0) > 20:
        tips.append("High churn rate — investigate uninstall reasons")
    if kpis.get("avg_rating", 5) < 3.5:
        tips.append("Low average rating — improve app quality guidelines")
    return tips or ["Marketplace metrics look healthy!"]
