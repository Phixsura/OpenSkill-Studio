"""Platform Roadmap — track and display platform development roadmap.

Manages roadmap items with status, voting, milestones, and ETA tracking.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RoadmapItem:
    item_id: str
    title: str
    description: str
    status: str  # planned, in_progress, completed, cancelled
    category: str
    votes: int = 0
    eta: str = ""
    milestone: str = ""


class PlatformRoadmapService:
    """Manages platform development roadmap."""

    def __init__(self):
        self._items: dict[str, RoadmapItem] = {}

    def add(self, item_id: str, title: str, description: str,
            category: str, status: str = "planned",
            eta: str = "", milestone: str = "") -> RoadmapItem:
        item = RoadmapItem(item_id=item_id, title=title, description=description,
                           status=status, category=category, eta=eta, milestone=milestone)
        self._items[item_id] = item
        return item

    def vote(self, item_id: str) -> int:
        item = self._items.get(item_id)
        if item:
            item.votes += 1
            return item.votes
        return 0

    def update_status(self, item_id: str, status: str) -> bool:
        item = self._items.get(item_id)
        if item:
            item.status = status
            return True
        return False

    def get_by_status(self, status: str) -> list[RoadmapItem]:
        return sorted([i for i in self._items.values() if i.status == status],
                      key=lambda i: i.votes, reverse=True)

    def get_by_milestone(self, milestone: str) -> list[RoadmapItem]:
        return [i for i in self._items.values() if i.milestone == milestone]

    def get_stats(self) -> dict:
        counts: dict[str, int] = defaultdict(int)
        for i in self._items.values():
            counts[i.status] += 1
        return {"total": len(self._items), "by_status": dict(counts),
                "total_votes": sum(i.votes for i in self._items.values())}
