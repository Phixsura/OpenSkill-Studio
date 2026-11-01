"""App API Traffic Split — split traffic between API versions.

Manages traffic splitting:
- Define splits with percentage weights
- Route requests based on split config
- Track traffic per version
- Per-installation scoped splits
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TrafficTarget:
    """A traffic split target."""

    version: str
    weight: int  # percentage 0-100
    request_count: int = 0


@dataclass
class TrafficSplit:
    """A traffic split configuration."""

    split_id: str
    targets: list[TrafficTarget]


class AppAPITrafficSplit:
    """Split traffic between API versions."""

    def __init__(self) -> None:
        self._splits: dict[tuple[str, str], TrafficSplit] = {}

    def create_split(
        self, installation_id: str, split_id: str, targets: list[dict],
    ) -> TrafficSplit:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not targets:
            raise ValueError("at least one target required")

        total = sum(t["weight"] for t in targets)
        if total != 100:
            raise ValueError(f"weights must sum to 100, got {total}")

        target_objs = [TrafficTarget(version=t["version"], weight=t["weight"]) for t in targets]
        split = TrafficSplit(split_id=split_id, targets=target_objs)
        self._splits[(installation_id, split_id)] = split
        return split

    def route(self, installation_id: str, split_id: str, request_id: str) -> str:
        """Deterministically route a request to a version."""
        split = self._get(installation_id, split_id)
        h = int(hashlib.sha256(request_id.encode()).hexdigest()[:8], 16) % 100

        cumulative = 0
        for target in split.targets:
            cumulative += target.weight
            if h < cumulative:
                target.request_count += 1
                return target.version

        split.targets[-1].request_count += 1
        return split.targets[-1].version

    def get_split(self, installation_id: str, split_id: str) -> TrafficSplit:
        return self._get(installation_id, split_id)

    def list_splits(self, installation_id: str) -> list[TrafficSplit]:
        return [s for (inst, _), s in self._splits.items() if inst == installation_id]

    def _get(self, installation_id: str, split_id: str) -> TrafficSplit:
        key = (installation_id, split_id)
        s = self._splits.get(key)
        if s is None:
            raise KeyError(f"Split {split_id} not found")
        return s
