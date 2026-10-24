"""Deployment rollback tracker — track rollbacks and their reasons."""
from __future__ import annotations
from collections import defaultdict


class RollbackTracker:
    def __init__(self):
        self._rollbacks: list[dict] = []

    def record(self, service: str, from_version: str, to_version: str,
               reason: str, triggered_by: str = "automated") -> dict:
        entry = {"service": service, "from": from_version, "to": to_version,
                 "reason": reason, "triggered_by": triggered_by}
        self._rollbacks.append(entry)
        return entry

    def by_reason(self) -> dict:
        reasons: dict[str, int] = defaultdict(int)
        for r in self._rollbacks:
            reasons[r["reason"]] += 1
        return dict(sorted(reasons.items(), key=lambda x: -x[1]))

    def by_service(self) -> dict:
        services: dict[str, int] = defaultdict(int)
        for r in self._rollbacks:
            services[r["service"]] += 1
        return dict(sorted(services.items(), key=lambda x: -x[1]))

    def stats(self) -> dict:
        auto = sum(1 for r in self._rollbacks if r["triggered_by"] == "automated")
        return {"total": len(self._rollbacks), "automated": auto,
                "manual": len(self._rollbacks) - auto}
