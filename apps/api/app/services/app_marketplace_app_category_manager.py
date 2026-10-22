"""Category manager — CRUD and hierarchy for marketplace categories."""

CATEGORIES = {
    "connector": {"label": "Connectors", "icon": "🔗", "parent": None},
    "automation": {"label": "Automation", "icon": "⚡", "parent": None},
    "analytics": {"label": "Analytics", "icon": "📊", "parent": None},
    "communication": {"label": "Communication", "icon": "💬", "parent": None},
    "developer_tools": {"label": "Developer Tools", "icon": "🛠️", "parent": None},
    "security": {"label": "Security", "icon": "🔒", "parent": None},
    "slack_connector": {"label": "Slack", "icon": "💬", "parent": "connector"},
    "github_connector": {"label": "GitHub", "icon": "🐙", "parent": "connector"},
}


def list_categories(*, include_children: bool = False) -> list[dict]:
    result = []
    for key, cat in CATEGORIES.items():
        if not include_children and cat["parent"]:
            continue
        result.append({"key": key, **cat})
    return result


def get_category_tree() -> list[dict]:
    roots = []
    for key, cat in CATEGORIES.items():
        if not cat["parent"]:
            children = [{"key": k, **c} for k, c in CATEGORIES.items() if c["parent"] == key]
            roots.append({"key": key, **cat, "children": children})
    return roots


def validate_category(*, category: str) -> bool:
    return category in CATEGORIES


def get_category_breadcrumb(*, category: str) -> list[dict]:
    crumbs = []
    current = category
    while current:
        cat = CATEGORIES.get(current)
        if not cat:
            break
        crumbs.insert(0, {"key": current, "label": cat["label"]})
        current = cat.get("parent")
    return crumbs
