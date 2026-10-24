"""Category page builder — compile category listing page data."""

CATEGORY_DESCRIPTIONS = {
    "connector": "Connect external systems — LMS, CRM, HRIS integrations",
    "automation": "Automate workflows with event-driven rules and AI",
    "analytics": "Build custom dashboards and reporting tools",
    "ui_extension": "Extend the platform with custom UI components",
    "ecosystem_source": "Import data from external talent ecosystems",
    "content_pack": "Bundle skills, projects, and workflows",
    "workflow_adapter": "Connect AI providers and execution engines",
}


def build_category_page(*, category: str, apps: list[dict], total: int, page: int, per_page: int) -> dict:
    return {
        "category": category,
        "description": CATEGORY_DESCRIPTIONS.get(category, ""),
        "apps": apps,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1,
    }
