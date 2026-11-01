"""API deprecation tracker — track deprecated endpoints and migration status."""
from __future__ import annotations


class ApiDeprecationTracker:
    def __init__(self):
        self._deprecated: dict[str, dict] = {}

    def deprecate(self, endpoint: str, sunset_date: str, replacement: str = "",
                  migration_guide: str = "") -> dict:
        self._deprecated[endpoint] = {"endpoint": endpoint, "sunset_date": sunset_date,
                                       "replacement": replacement,
                                       "migration_guide": migration_guide,
                                       "callers_migrated": 0, "total_callers": 0}
        return self._deprecated[endpoint]

    def track_usage(self, endpoint: str, caller: str, migrated: bool) -> dict:
        if endpoint in self._deprecated:
            self._deprecated[endpoint]["total_callers"] += 1
            if migrated:
                self._deprecated[endpoint]["callers_migrated"] += 1
        return {"endpoint": endpoint, "caller": caller, "migrated": migrated}

    def migration_status(self) -> list[dict]:
        results = []
        for ep, data in self._deprecated.items():
            total = data["total_callers"]
            migrated = data["callers_migrated"]
            pct = round(migrated / max(total, 1) * 100, 1)
            results.append({**data, "migration_pct": pct, "ready_to_sunset": pct >= 100})
        return sorted(results, key=lambda r: r["sunset_date"])

    def stats(self) -> dict:
        ready = sum(1 for r in self.migration_status() if r["ready_to_sunset"])
        return {"total_deprecated": len(self._deprecated), "ready_to_sunset": ready}
