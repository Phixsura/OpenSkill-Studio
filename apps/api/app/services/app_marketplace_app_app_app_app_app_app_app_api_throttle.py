"""API throttle manager — per-tenant API throttling with quotas."""
from __future__ import annotations
from collections import defaultdict
import time


class ApiThrottleManager:
    def __init__(self):
        self._quotas: dict[str, dict] = {}
        self._usage: dict[str, dict] = defaultdict(lambda: {"count": 0, "window_start": 0})

    def set_quota(self, tenant_id: str, requests_per_minute: int, burst: int = 0) -> dict:
        self._quotas[tenant_id] = {"rpm": requests_per_minute, "burst": burst}
        return {"tenant_id": tenant_id, "rpm": requests_per_minute, "burst": burst}

    def check(self, tenant_id: str, now: float | None = None) -> dict:
        now = now or time.time()
        quota = self._quotas.get(tenant_id, {"rpm": 60, "burst": 0})
        usage = self._usage[tenant_id]
        if now - usage["window_start"] >= 60:
            usage["count"] = 0
            usage["window_start"] = now
        limit = quota["rpm"] + quota["burst"]
        if usage["count"] >= limit:
            retry_after = round(60 - (now - usage["window_start"]), 1)
            return {"allowed": False, "tenant_id": tenant_id,
                    "retry_after_seconds": max(0, retry_after)}
        usage["count"] += 1
        remaining = limit - usage["count"]
        return {"allowed": True, "tenant_id": tenant_id,
                "remaining": remaining, "limit": limit}

    def usage_report(self) -> dict:
        report = []
        for tid, usage in self._usage.items():
            quota = self._quotas.get(tid, {"rpm": 60, "burst": 0})
            limit = quota["rpm"] + quota["burst"]
            pct = round(usage["count"] / max(limit, 1) * 100, 1)
            report.append({"tenant_id": tid, "used": usage["count"],
                           "limit": limit, "pct_used": pct})
        return {"tenants": sorted(report, key=lambda r: -r["pct_used"]),
                "total_tenants": len(report)}
