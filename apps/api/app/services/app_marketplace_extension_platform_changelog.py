"""Platform Changelog — track platform-level changes and updates."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class PlatformChange:
    change_id: str
    version: str
    title: str
    description: str
    category: str = "feature"  # feature, improvement, fix, breaking, security
    date: str = ""
    def __post_init__(self):
        if not self.date: self.date = time.strftime("%Y-%m-%d")


class PlatformChangelogService:
    def __init__(self):
        self._changes: list[PlatformChange] = []
        self._counter = 0

    def add(self, version: str, title: str, description: str,
            category: str = "feature") -> PlatformChange:
        self._counter += 1
        c = PlatformChange(change_id=f"pc-{self._counter}", version=version,
                           title=title, description=description, category=category)
        self._changes.append(c)
        return c

    def get_by_version(self, version: str) -> list[PlatformChange]:
        return [c for c in self._changes if c.version == version]

    def get_latest(self, limit: int = 20) -> list[PlatformChange]:
        return list(reversed(self._changes))[:limit]

    def get_breaking(self) -> list[PlatformChange]:
        return [c for c in self._changes if c.category == "breaking"]
