"""Multi-region failover — manage primary/secondary regions with health-based failover."""
from __future__ import annotations


class MultiRegionManager:
    def __init__(self):
        self._regions: dict[str, dict] = {}
        self._primary: str = ""

    def add_region(self, region_id: str, *, label: str, is_primary: bool = False) -> dict:
        self._regions[region_id] = {"id": region_id, "label": label,
                                     "healthy": True, "traffic_pct": 0}
        if is_primary or not self._primary:
            self._primary = region_id
        self._rebalance()
        return {"region": region_id, "primary": self._primary}

    def update_health(self, region_id: str, *, healthy: bool) -> dict:
        r = self._regions.get(region_id)
        if not r:
            return {"error": "Region not found"}
        r["healthy"] = healthy
        if not healthy and region_id == self._primary:
            self._failover()
        self._rebalance()
        return {"region": region_id, "healthy": healthy, "primary": self._primary}

    def status(self) -> dict:
        healthy_count = sum(1 for r in self._regions.values() if r["healthy"])
        return {
            "primary": self._primary, "total_regions": len(self._regions),
            "healthy_regions": healthy_count,
            "status": "healthy" if healthy_count == len(self._regions) else "degraded" if healthy_count > 0 else "down",
            "regions": list(self._regions.values()),
        }

    def _failover(self) -> None:
        for rid, r in self._regions.items():
            if r["healthy"] and rid != self._primary:
                self._primary = rid
                return

    def _rebalance(self) -> None:
        healthy = [r for r in self._regions.values() if r["healthy"]]
        for r in self._regions.values():
            r["traffic_pct"] = round(100 / max(len(healthy), 1)) if r["healthy"] else 0
