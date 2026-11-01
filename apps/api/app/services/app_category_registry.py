"""App category registry — dynamic category management.

Extends the static VALID_CATEGORIES with metadata, icons, and descriptions.
"""

from dataclasses import dataclass


@dataclass
class CategoryInfo:
    key: str
    label: str
    icon: str
    description: str
    max_apps: int = 0  # 0 = unlimited


CATEGORIES: dict[str, CategoryInfo] = {
    "connector": CategoryInfo("connector", "Connector", "🔌", "LMS, CRM, HRIS integrations"),
    "automation": CategoryInfo("automation", "Automation", "🤖", "Event-driven workflows and auto-grading"),
    "analytics": CategoryInfo("analytics", "Analytics", "📊", "Reporting, dashboards, and insights"),
    "ui_extension": CategoryInfo("ui_extension", "UI Extension", "🖥️", "Dashboard cards, sidebars, panels"),
    "ecosystem_source": CategoryInfo("ecosystem_source", "Ecosystem Source", "🌐", "External data sources"),
    "content_pack": CategoryInfo("content_pack", "Content Pack", "📦", "Skill and workflow bundles"),
    "workflow_adapter": CategoryInfo("workflow_adapter", "Workflow Adapter", "⚡", "AI provider adapters"),
}


def get_category(key: str) -> CategoryInfo | None:
    return CATEGORIES.get(key)


def list_categories() -> list[CategoryInfo]:
    return list(CATEGORIES.values())


def get_category_keys() -> list[str]:
    return sorted(CATEGORIES.keys())
