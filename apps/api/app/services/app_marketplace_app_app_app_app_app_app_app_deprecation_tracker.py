"""API deprecation tracker — track deprecated endpoints and migration progress."""
from __future__ import annotations


class DeprecationTracker:
    def __init__(self):
        self._deprecated: dict[str, dict] = {}

    def deprecate(self, endpoint: str, *, sunset_date: str, replacement: str,
                   reason: str = "", migration_guide_url: str = "") -> dict:
        self._deprecated[endpoint] = {
            "endpoint": endpoint, "sunset_date": sunset_date,
            "replacement": replacement, "reason": reason,
            "migration_guide_url": migration_guide_url,
            "callers_migrated": 0, "callers_total": 0,
        }
        return {"deprecated": endpoint, "sunset_date": sunset_date, "replacement": replacement}

    def track_usage(self, endpoint: str, *, total_callers: int, migrated: int) -> dict:
        d = self._deprecated.get(endpoint)
        if not d:
            return {"error": "Endpoint not tracked"}
        d["callers_total"] = total_callers
        d["callers_migrated"] = migrated
        pct = round(migrated / max(total_callers, 1) * 100)
        return {"endpoint": endpoint, "migration_pct": pct,
                "remaining": total_callers - migrated}

    def summary(self) -> dict:
        items = []
        for d in self._deprecated.values():
            total = d["callers_total"]
            migrated = d["callers_migrated"]
            pct = round(migrated / max(total, 1) * 100)
            items.append({**d, "migration_pct": pct, "remaining": total - migrated,
                          "ready_to_sunset": pct == 100})
        return {"total_deprecated": len(items), "items": items,
                "ready_to_sunset": sum(1 for i in items if i["ready_to_sunset"])}
