"""App API Developer Portal Navigation — manage developer portal navigation structure."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class NavItem:
    item_id: str
    label: str
    path: str
    icon: str = ""
    parent_id: str | None = None
    order: int = 0
    visible: bool = True

class AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], NavItem] = {}

    def add_item(self, installation_id: str, item_id: str, label: str, path: str, icon: str = "", parent_id: str | None = None, order: int = 0) -> NavItem:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, item_id)
        if key in self._items: raise ValueError(f"Item {item_id} exists")
        n = NavItem(item_id=item_id, label=label, path=path, icon=icon, parent_id=parent_id, order=order)
        self._items[key] = n
        return n

    def toggle_visibility(self, installation_id: str, item_id: str, visible: bool) -> NavItem:
        key = (installation_id, item_id)
        n = self._items.get(key)
        if n is None: raise KeyError(f"Item {item_id} not found")
        n.visible = visible
        return n

    def top_level(self, installation_id: str) -> list[NavItem]:
        items = [n for (inst, _), n in self._items.items() if inst == installation_id and n.parent_id is None and n.visible]
        return sorted(items, key=lambda n: n.order)

    def children_of(self, installation_id: str, parent_id: str) -> list[NavItem]:
        items = [n for (inst, _), n in self._items.items() if inst == installation_id and n.parent_id == parent_id and n.visible]
        return sorted(items, key=lambda n: n.order)

    def all_items(self, installation_id: str) -> list[NavItem]:
        return sorted([n for (inst, _), n in self._items.items() if inst == installation_id], key=lambda n: n.order)
