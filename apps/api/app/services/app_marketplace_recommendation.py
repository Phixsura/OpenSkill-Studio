"""Marketplace recommendation — recommend apps based on org usage patterns."""


def recommend_apps(*, installed_categories: list[str], available_apps: list[dict], limit: int = 5) -> list[dict]:
    """Recommend apps based on what categories the org already uses."""
    installed_set = set(installed_categories)
    # Prefer same categories, then related
    RELATED = {"connector": ["automation"], "automation": ["connector", "analytics"],
               "analytics": ["ui_extension"], "ui_extension": ["analytics"]}
    
    scores: list[tuple[float, dict]] = []
    for app in available_apps:
        cat = app.get("category", "")
        score = 0.0
        if cat in installed_set:
            score += 10  # Same category
        for installed_cat in installed_set:
            if cat in RELATED.get(installed_cat, []):
                score += 5  # Related category
        score += app.get("install_count", 0) * 0.01  # Popularity boost
        if score > 0:
            scores.append((score, app))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    return [app for _, app in scores[:limit]]
