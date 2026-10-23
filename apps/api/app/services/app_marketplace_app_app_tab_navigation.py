"""Tab navigation — tabbed interface for app detail pages."""


def build_tab_config(*, app_id: str, has_docs: bool = True, has_reviews: bool = True,
                       is_developer: bool = False) -> dict:
    tabs = [
        {"id": "overview", "label": "Overview", "icon": "📋"},
        {"id": "versions", "label": "Versions", "icon": "📦"},
    ]
    if has_reviews:
        tabs.append({"id": "reviews", "label": "Reviews", "icon": "⭐"})
    if has_docs:
        tabs.append({"id": "docs", "label": "Documentation", "icon": "📚"})
    tabs.append({"id": "changelog", "label": "Changelog", "icon": "📝"})
    if is_developer:
        tabs.extend([
            {"id": "analytics", "label": "Analytics", "icon": "📊"},
            {"id": "settings", "label": "Settings", "icon": "⚙️"},
        ])
    return {"tabs": tabs, "total": len(tabs), "default_tab": "overview"}
