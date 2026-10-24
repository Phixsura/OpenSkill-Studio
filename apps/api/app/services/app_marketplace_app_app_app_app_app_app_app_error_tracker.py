"""Error tracker — track, group, and analyze application errors."""
from __future__ import annotations
from collections import defaultdict


class ErrorTracker:
    def __init__(self):
        self._errors: list[dict] = []
        self._groups: dict[str, dict] = defaultdict(lambda: {"count": 0, "last_seen": 0})

    def track(self, error_type: str, message: str, stack: str = "", service: str = "") -> dict:
        group_key = f"{error_type}:{message[:50]}"
        self._groups[group_key]["count"] += 1
        entry = {"type": error_type, "message": message, "stack": stack,
                 "service": service, "group": group_key}
        self._errors.append(entry)
        return {"tracked": True, "group": group_key, "occurrences": self._groups[group_key]["count"]}

    def top_errors(self, limit: int = 10) -> list[dict]:
        sorted_groups = sorted(self._groups.items(), key=lambda x: -x[1]["count"])[:limit]
        return [{"group": k, "count": v["count"]} for k, v in sorted_groups]

    def stats(self) -> dict:
        return {"total_errors": len(self._errors), "unique_groups": len(self._groups)}
