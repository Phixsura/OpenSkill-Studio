"""Documentation sitemap — structured navigation tree for docs."""
from __future__ import annotations

DOC_TREE = [
    {"slug": "getting-started", "title": "Getting Started", "children": [
        {"slug": "quickstart", "title": "Quickstart"},
        {"slug": "installation", "title": "Installation"},
        {"slug": "first-app", "title": "Your First App"},
    ]},
    {"slug": "api-reference", "title": "API Reference", "children": [
        {"slug": "authentication", "title": "Authentication"},
        {"slug": "apps", "title": "Apps API"},
        {"slug": "webhooks", "title": "Webhooks API"},
        {"slug": "analytics", "title": "Analytics API"},
    ]},
    {"slug": "guides", "title": "Guides", "children": [
        {"slug": "deployment", "title": "Deployment"},
        {"slug": "security", "title": "Security Best Practices"},
        {"slug": "monitoring", "title": "Monitoring"},
    ]},
]


def get_sitemap() -> list[dict]:
    return DOC_TREE


def find_doc(slug: str) -> dict | None:
    for section in DOC_TREE:
        if section["slug"] == slug:
            return section
        for child in section.get("children", []):
            if child["slug"] == slug:
                return {**child, "parent": section["slug"]}
    return None


def get_breadcrumbs(slug: str) -> list[dict]:
    crumbs = [{"slug": "", "title": "Docs"}]
    for section in DOC_TREE:
        if section["slug"] == slug:
            crumbs.append({"slug": section["slug"], "title": section["title"]})
            return crumbs
        for child in section.get("children", []):
            if child["slug"] == slug:
                crumbs.append({"slug": section["slug"], "title": section["title"]})
                crumbs.append({"slug": child["slug"], "title": child["title"]})
                return crumbs
    return crumbs
