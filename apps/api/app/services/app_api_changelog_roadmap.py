"""App API Changelog Roadmap — track upcoming features and releases."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import structlog

log = structlog.get_logger()

class RoadmapStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class RoadmapItem:
    item_id: str
    title: str
    description: str
    target_version: str
    status: RoadmapStatus = RoadmapStatus.PLANNED
    vote_count: int = 0

class AppAPIChangelogRoadmap:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], RoadmapItem] = {}

    def add_item(self, installation_id: str, item_id: str, title: str, description: str, target_version: str) -> RoadmapItem:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, item_id)
        if key in self._items: raise ValueError(f"Item {item_id} already exists")
        item = RoadmapItem(item_id=item_id, title=title, description=description, target_version=target_version)
        self._items[key] = item
        return item

    def update_status(self, installation_id: str, item_id: str, status: RoadmapStatus) -> RoadmapItem:
        item = self._get(installation_id, item_id)
        item.status = status
        return item

    def vote(self, installation_id: str, item_id: str) -> RoadmapItem:
        item = self._get(installation_id, item_id)
        item.vote_count += 1
        return item

    def by_status(self, installation_id: str, status: RoadmapStatus) -> list[RoadmapItem]:
        return [i for (inst, _), i in self._items.items() if inst == installation_id and i.status == status]

    def list_items(self, installation_id: str) -> list[RoadmapItem]:
        return [i for (inst, _), i in self._items.items() if inst == installation_id]

    def _get(self, installation_id: str, item_id: str) -> RoadmapItem:
        i = self._items.get((installation_id, item_id))
        if i is None: raise KeyError(f"Item {item_id} not found")
        return i
