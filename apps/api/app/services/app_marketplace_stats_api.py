"""Marketplace stats API — public statistics for the platform."""


def get_public_stats(*, apps: list[dict], developers: list[dict], installs: list[dict]) -> dict:
    published = sum(1 for a in apps if a.get("status") == "published")
    verified_devs = sum(1 for d in developers if d.get("verified"))
    active_installs = sum(1 for i in installs if i.get("status") == "active")
    categories = len(set(a.get("category") for a in apps if a.get("category")))
    return {
        "total_apps": len(apps), "published_apps": published,
        "total_developers": len(developers), "verified_developers": verified_devs,
        "total_installs": len(installs), "active_installs": active_installs,
        "categories": categories,
    }


def get_growth_metrics(*, current: dict, previous: dict) -> dict:
    metrics = {}
    for key in ("total_apps", "total_developers", "total_installs"):
        cur = current.get(key, 0)
        prev = previous.get(key, 0)
        change = cur - prev
        pct = round(change / max(prev, 1) * 100, 1)
        metrics[key] = {"current": cur, "previous": prev, "change": change, "change_pct": pct}
    return metrics


def build_stats_response(*, stats: dict, growth: dict) -> dict:
    return {"data": stats, "growth": growth, "generated_at": "now",
            "highlights": [
                f"{stats.get('published_apps', 0)} published apps",
                f"{stats.get('verified_developers', 0)} verified developers",
                f"{stats.get('active_installs', 0)} active installations",
            ]}
