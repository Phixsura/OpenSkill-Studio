"""Extension Status Tracker — track extension lifecycle status."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class StatusEntry:
    extension_id: str
    status: str  # draft, review, active, suspended, archived
    reason: str = ""

class ExtensionStatusTrackerService:
    def __init__(self):
        self._statuses: dict[str, StatusEntry] = {}

    def set_status(self, extension_id: str, status: str, reason: str = "") -> StatusEntry:
        entry = StatusEntry(extension_id=extension_id, status=status, reason=reason)
        self._statuses[extension_id] = entry
        return entry

    def get_status(self, extension_id: str) -> str:
        return self._statuses.get(extension_id, StatusEntry("", "unknown")).status

    def get_by_status(self, status: str) -> list[str]:
        return [eid for eid, e in self._statuses.items() if e.status == status]

    def get_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for e in self._statuses.values():
            counts[e.status] += 1
        return dict(counts)
