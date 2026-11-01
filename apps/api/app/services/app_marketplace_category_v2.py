"""Marketplace category v2 — hierarchical categories with metadata and counts."""

CATEGORY_TREE = {
    "connectors": {"label": "Connectors", "icon": "🔗", "children": {
        "crm": {"label": "CRM", "icon": "📇"},
        "communication": {"label": "Communication", "icon": "💬"},
        "storage": {"label": "Storage", "icon": "💾"},
        "devtools": {"label": "Dev Tools", "icon": "🛠️"},
    }},
    "automation": {"label": "Automation", "icon": "⚡", "children": {
        "workflows": {"label": "Workflows", "icon": "📋"},
        "scheduling": {"label": "Scheduling", "icon": "⏰"},
    }},
    "analytics": {"label": "Analytics", "icon": "📊", "children": {
        "dashboards": {"label": "Dashboards", "icon": "📈"},
        "reporting": {"label": "Reporting", "icon": "📄"},
    }},
}


def get_category_tree() -> list[dict]:
    result = []
    for key, cat in CATEGORY_TREE.items():
        children = [{"id": ck, **cv} for ck, cv in cat.get("children", {}).items()]
        result.append({"id": key, "label": cat["label"], "icon": cat["icon"],
                        "children": children, "child_count": len(children)})
    return result


def get_category_breadcrumb(*, category_id: str) -> list[dict]:
    for parent_id, parent in CATEGORY_TREE.items():
        if parent_id == category_id:
            return [{"id": parent_id, "label": parent["label"]}]
        for child_id, child in parent.get("children", {}).items():
            if child_id == category_id:
                return [{"id": parent_id, "label": parent["label"]},
                        {"id": child_id, "label": child["label"]}]
    return []


def count_apps_by_category(*, apps: list[dict]) -> dict:
    counts = {}
    for a in apps:
        cat = a.get("category", "other")
        counts[cat] = counts.get(cat, 0) + 1
    return counts
