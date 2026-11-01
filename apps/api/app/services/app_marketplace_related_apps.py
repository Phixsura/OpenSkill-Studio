"""Related apps — recommend similar apps based on category, tags, and usage."""

from collections import defaultdict


def find_related_by_category(*, app: dict, all_apps: list[dict], limit: int = 6) -> list[dict]:
    category = app.get("category")
    return [a for a in all_apps if a.get("category") == category and a.get("id") != app.get("id")][:limit]


def find_related_by_tags(*, app: dict, all_apps: list[dict], limit: int = 6) -> list[dict]:
    app_tags = set(app.get("tags", []))
    if not app_tags:
        return []
    scored = []
    for a in all_apps:
        if a.get("id") == app.get("id"):
            continue
        overlap = len(app_tags & set(a.get("tags", [])))
        if overlap > 0:
            scored.append((overlap, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored[:limit]]


def find_also_installed(*, app_id: str, install_pairs: list[dict], limit: int = 6) -> list[dict]:
    co_installed = defaultdict(int)
    for pair in install_pairs:
        if pair.get("app_a") == app_id:
            co_installed[pair["app_b"]] += 1
        elif pair.get("app_b") == app_id:
            co_installed[pair["app_a"]] += 1
    return [{"app_id": aid, "co_install_count": cnt} for aid, cnt in
            sorted(co_installed.items(), key=lambda x: -x[1])[:limit]]


def build_related_section(*, by_category: list[dict], by_tags: list[dict],
                             also_installed: list[dict]) -> dict:
    return {"sections": [
        {"key": "category", "title": "Similar Apps", "apps": by_category, "count": len(by_category)},
        {"key": "tags", "title": "Apps with Similar Tags", "apps": by_tags, "count": len(by_tags)},
        {"key": "also_installed", "title": "Often Installed Together", "apps": also_installed, "count": len(also_installed)},
    ]}
