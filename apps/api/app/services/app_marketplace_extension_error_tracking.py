"""Extension Error Tracking — collect and aggregate extension runtime errors."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class ErrorEvent:
    error_id: str
    extension_id: str
    error_type: str
    message: str
    stack_trace: str = ""
    user_id: str = ""
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class ErrorGroup:
    fingerprint: str
    error_type: str
    message: str
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    resolved: bool = False


class ExtErrorTrackingService:
    def __init__(self):
        self._events: list[ErrorEvent] = []
        self._groups: dict[str, dict[str, ErrorGroup]] = {}  # ext_id -> {fingerprint -> group}
        self._counter = 0

    def _fingerprint(self, error_type: str, message: str) -> str:
        return f"{error_type}:{message[:100]}"

    def report(self, extension_id: str, error_type: str, message: str,
               stack_trace: str = "", user_id: str = "") -> ErrorEvent:
        self._counter += 1
        evt = ErrorEvent(error_id=f"err-{self._counter}", extension_id=extension_id,
                         error_type=error_type, message=message,
                         stack_trace=stack_trace, user_id=user_id)
        self._events.append(evt)
        fp = self._fingerprint(error_type, message)
        if extension_id not in self._groups:
            self._groups[extension_id] = {}
        grp = self._groups[extension_id].get(fp)
        if grp:
            grp.count += 1
            grp.last_seen = evt.timestamp
        else:
            self._groups[extension_id][fp] = ErrorGroup(
                fingerprint=fp, error_type=error_type, message=message,
                count=1, first_seen=evt.timestamp, last_seen=evt.timestamp)
        return evt

    def get_groups(self, extension_id: str, unresolved_only: bool = True) -> list[ErrorGroup]:
        groups = list(self._groups.get(extension_id, {}).values())
        if unresolved_only:
            groups = [g for g in groups if not g.resolved]
        return sorted(groups, key=lambda g: g.count, reverse=True)

    def resolve(self, extension_id: str, fingerprint: str) -> bool:
        grp = self._groups.get(extension_id, {}).get(fingerprint)
        if grp:
            grp.resolved = True
            return True
        return False

    def get_error_rate(self, extension_id: str) -> int:
        return sum(g.count for g in self._groups.get(extension_id, {}).values()
                   if not g.resolved)
