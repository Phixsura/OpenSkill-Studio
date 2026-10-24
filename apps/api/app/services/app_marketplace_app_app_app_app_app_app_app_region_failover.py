"""Multi-region failover coordinator — coordinate failover across regions."""
from __future__ import annotations


class RegionFailoverCoordinator:
    def __init__(self):
        self._regions: dict[str, dict] = {}
        self._primary: str = ""

    def register_region(self, name: str, is_primary: bool = False) -> dict:
        self._regions[name] = {"name": name, "status": "active", "is_primary": is_primary}
        if is_primary:
            self._primary = name
        return self._regions[name]

    def failover(self, failed_region: str) -> dict:
        self._regions[failed_region]["status"] = "failed"
        candidates = [r for r in self._regions.values() if r["status"] == "active" and r["name"] != failed_region]
        if not candidates:
            return {"success": False, "reason": "no_healthy_regions"}
        new_primary = candidates[0]["name"]
        self._regions[new_primary]["is_primary"] = True
        self._primary = new_primary
        return {"success": True, "failed": failed_region, "new_primary": new_primary}

    def failback(self, region: str) -> dict:
        self._regions[region]["status"] = "active"
        return {"region": region, "status": "active"}

    def status(self) -> dict:
        active = sum(1 for r in self._regions.values() if r["status"] == "active")
        return {"total_regions": len(self._regions), "active": active,
                "primary": self._primary,
                "failed": [r["name"] for r in self._regions.values() if r["status"] == "failed"]}
