"""Developer changelog RSS v2 — per-developer feed across all their apps."""


def build_developer_feed(*, developer: dict, app_updates: list[dict]) -> dict:
    entries = []
    for u in sorted(app_updates, key=lambda x: x.get("released_at", ""), reverse=True):
        entries.append({
            "title": f"{u['app_name']} v{u['version']}",
            "app_slug": u.get("app_slug"),
            "released_at": u.get("released_at"),
            "notes": u.get("release_notes", ""),
        })
    return {
        "feed_title": f"{developer.get('display_name', 'Developer')} — App Updates",
        "entries": entries[:20],
        "entry_count": min(len(entries), 20),
    }


def compute_release_frequency(*, releases: list[dict]) -> dict:
    if len(releases) < 2:
        return {"avg_days_between": 0, "frequency": "unknown"}
    dates = sorted(r.get("released_at", "") for r in releases)
    # Simplified: count entries per period
    return {"total_releases": len(releases),
            "frequency": "weekly" if len(releases) > 12 else "monthly" if len(releases) > 4 else "quarterly"}
