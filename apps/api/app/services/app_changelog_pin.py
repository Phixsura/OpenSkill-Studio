"""App Changelog Pin — pin important changelog entries for visibility.

Manages pinned changelog entries:
- Pin/unpin entries
- List pinned entries across versions
- Max pin limit enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PinnedEntry:
    """A pinned changelog entry."""

    entry_id: str
    version: str
    title: str
    reason: str = ""
    pinned_by: str = ""


class AppChangelogPin:
    """Pin important changelog entries."""

    def __init__(self, max_pins: int = 10) -> None:
        self._max = max(1, max_pins)
        # installation_id → list[PinnedEntry]
        self._pins: dict[str, list[PinnedEntry]] = {}

    def pin(
        self,
        installation_id: str,
        entry_id: str,
        version: str,
        title: str,
        reason: str = "",
        pinned_by: str = "",
    ) -> PinnedEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not entry_id:
            raise ValueError("entry_id is required")

        pins = self._pins.setdefault(installation_id, [])

        # Check duplicate
        if any(p.entry_id == entry_id for p in pins):
            raise ValueError(f"Entry {entry_id} already pinned")

        if len(pins) >= self._max:
            raise ValueError(f"Maximum {self._max} pins reached")

        entry = PinnedEntry(
            entry_id=entry_id, version=version, title=title,
            reason=reason, pinned_by=pinned_by,
        )
        pins.append(entry)
        return entry

    def unpin(self, installation_id: str, entry_id: str) -> bool:
        pins = self._pins.get(installation_id, [])
        before = len(pins)
        self._pins[installation_id] = [p for p in pins if p.entry_id != entry_id]
        return len(self._pins[installation_id]) < before

    def list_pins(self, installation_id: str) -> list[PinnedEntry]:
        return list(self._pins.get(installation_id, []))

    def is_pinned(self, installation_id: str, entry_id: str) -> bool:
        return any(p.entry_id == entry_id for p in self._pins.get(installation_id, []))

    def pin_count(self, installation_id: str) -> int:
        return len(self._pins.get(installation_id, []))
