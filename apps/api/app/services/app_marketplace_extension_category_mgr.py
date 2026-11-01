"""Extension Category Manager — hierarchical categories for marketplace."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Category:
    category_id: str
    name: str
    slug: str
    parent_id: str = ""
    icon: str = "📦"
    description: str = ""
    extension_count: int = 0


class ExtCategoryMgrService:
    def __init__(self):
        self._categories: dict[str, Category] = {}
        self._seed()

    def _seed(self):
        defaults = [
            ("dev-tools", "Developer Tools", "developer-tools", "", "🛠️"),
            ("analytics", "Analytics", "analytics", "", "📊"),
            ("integrations", "Integrations", "integrations", "", "🔗"),
            ("ui", "UI Components", "ui-components", "", "🎨"),
            ("security", "Security", "security", "", "🔒"),
            ("automation", "Automation", "automation", "", "⚡"),
        ]
        for cid, name, slug, parent, icon in defaults:
            self._categories[cid] = Category(category_id=cid, name=name,
                                             slug=slug, parent_id=parent, icon=icon)

    def create(self, category_id: str, name: str, slug: str,
               parent_id: str = "", icon: str = "📦") -> Category:
        if parent_id and parent_id not in self._categories:
            raise ValueError("Parent category not found")
        c = Category(category_id=category_id, name=name, slug=slug,
                     parent_id=parent_id, icon=icon)
        self._categories[category_id] = c
        return c

    def get_tree(self) -> list[dict]:
        roots = [c for c in self._categories.values() if not c.parent_id]
        tree = []
        for r in sorted(roots, key=lambda c: c.name):
            children = [c for c in self._categories.values() if c.parent_id == r.category_id]
            tree.append({"category": r, "children": sorted(children, key=lambda c: c.name)})
        return tree

    def get_all(self) -> list[Category]:
        return list(self._categories.values())

    def increment_count(self, category_id: str) -> bool:
        c = self._categories.get(category_id)
        if c:
            c.extension_count += 1
            return True
        return False

    def get_by_slug(self, slug: str) -> Category | None:
        return next((c for c in self._categories.values() if c.slug == slug), None)
