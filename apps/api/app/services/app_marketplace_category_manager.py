"""Category Manager — manage marketplace categories and taxonomy.

Provides hierarchical category management with parent/child relationships,
ordering, icons, and extension counting per category.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Category:
    slug: str
    name: str
    description: str
    icon: str = "📦"
    parent_slug: str | None = None
    order: int = 0
    featured: bool = False


class CategoryManager:
    """Manages marketplace category taxonomy."""

    def __init__(self):
        self._categories: dict[str, Category] = {}
        self._ext_counts: dict[str, int] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = [
            Category("tools", "Developer Tools", "Code utilities and productivity", "🛠️", order=1),
            Category("connectors", "Connectors", "Integrations with external services", "🔌", order=2, featured=True),
            Category("themes", "Themes", "Visual customization", "🎨", order=3),
            Category("analytics", "Analytics", "Data insights and reporting", "📊", order=4),
            Category("automation", "Automation", "Workflow automation rules", "⚙️", order=5, featured=True),
            Category("security", "Security", "Security and compliance tools", "🔒", order=6),
            Category("testing", "Testing", "Test frameworks and utilities", "🧪", order=7),
            Category("ui", "UI Components", "Dashboard widgets and components", "🧩", order=8),
        ]
        for cat in defaults:
            self._categories[cat.slug] = cat

    def add_category(self, category: Category) -> Category:
        self._categories[category.slug] = category
        return category

    def get_category(self, slug: str) -> Category | None:
        return self._categories.get(slug)

    def remove_category(self, slug: str) -> bool:
        # Don't remove if it has children
        if any(c.parent_slug == slug for c in self._categories.values()):
            return False
        return self._categories.pop(slug, None) is not None

    def list_categories(self, parent_slug: str | None = None, featured_only: bool = False) -> list[Category]:
        cats = [c for c in self._categories.values() if c.parent_slug == parent_slug]
        if featured_only:
            cats = [c for c in cats if c.featured]
        return sorted(cats, key=lambda c: c.order)

    def get_children(self, parent_slug: str) -> list[Category]:
        return self.list_categories(parent_slug=parent_slug)

    def get_breadcrumb(self, slug: str) -> list[Category]:
        """Get category path from root to this category."""
        path = []
        current = self._categories.get(slug)
        while current:
            path.append(current)
            current = self._categories.get(current.parent_slug) if current.parent_slug else None
        return list(reversed(path))

    def update_count(self, slug: str, count: int) -> None:
        self._ext_counts[slug] = count

    def get_count(self, slug: str) -> int:
        return self._ext_counts.get(slug, 0)

    def get_tree(self) -> list[dict]:
        """Get full category tree as nested dicts."""
        def build(parent: str | None) -> list[dict]:
            children = self.list_categories(parent_slug=parent)
            return [{
                "slug": c.slug, "name": c.name, "icon": c.icon,
                "count": self.get_count(c.slug),
                "children": build(c.slug),
            } for c in children]
        return build(None)
