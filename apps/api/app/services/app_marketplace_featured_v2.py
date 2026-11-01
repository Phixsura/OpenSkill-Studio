"""Featured apps v2 — algorithmic featuring with editorial picks and trending."""

from collections import defaultdict


def compute_trending_score(*, app: dict, period_days: int = 7) -> float:
    installs = app.get("recent_installs", 0)
    reviews = app.get("recent_reviews", 0)
    rating = app.get("avg_rating", 0)
    return round(installs * 2 + reviews * 5 + rating * 10, 1)


def select_featured_apps(*, apps: list[dict], editorial_picks: list[str],
                            max_featured: int = 12) -> dict:
    # Editorial picks first
    featured = []
    remaining = []
    for app in apps:
        if app.get("id") in editorial_picks:
            featured.append({**app, "featured_reason": "editorial_pick"})
        else:
            remaining.append(app)
    # Fill with trending
    scored = sorted(remaining, key=lambda a: compute_trending_score(app=a), reverse=True)
    for app in scored:
        if len(featured) >= max_featured:
            break
        featured.append({**app, "featured_reason": "trending"})
    return {"featured": featured, "count": len(featured),
            "editorial_count": sum(1 for f in featured if f["featured_reason"] == "editorial_pick"),
            "trending_count": sum(1 for f in featured if f["featured_reason"] == "trending")}


def build_featured_section(*, featured: list[dict], title: str = "Featured Apps") -> dict:
    hero = featured[0] if featured else None
    grid = featured[1:5] if len(featured) > 1 else []
    rest = featured[5:] if len(featured) > 5 else []
    return {"title": title, "hero": hero, "grid": grid, "rest": rest, "total": len(featured)}
