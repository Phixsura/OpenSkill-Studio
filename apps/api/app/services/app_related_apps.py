"""Related apps — find apps related to a given app."""


def find_related(*, app: dict, all_apps: list[dict], limit: int = 5) -> list[dict]:
    """Find related apps by category and permission overlap."""
    app_id = app.get("id")
    app_cat = app.get("category", "")
    app_perms = set(app.get("permissions", []))
    
    scored = []
    for other in all_apps:
        if other.get("id") == app_id:
            continue
        score = 0
        if other.get("category") == app_cat:
            score += 10
        other_perms = set(other.get("permissions", []))
        score += len(app_perms & other_perms) * 2
        score += other.get("install_count", 0) * 0.01
        if score > 0:
            scored.append((score, other))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [app for _, app in scored[:limit]]
