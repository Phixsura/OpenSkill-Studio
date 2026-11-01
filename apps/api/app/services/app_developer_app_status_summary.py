"""App status summary — build status overview for all developer apps."""


def build_status_summary(apps: list[dict]) -> dict:
    statuses = {}
    for app in apps:
        status = app.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
    
    total = len(apps)
    published = statuses.get("published", 0)
    return {
        "total": total,
        "by_status": statuses,
        "published_pct": round(published / total * 100, 1) if total > 0 else 0,
        "needs_attention": statuses.get("rejected", 0) + statuses.get("revoked", 0),
    }
