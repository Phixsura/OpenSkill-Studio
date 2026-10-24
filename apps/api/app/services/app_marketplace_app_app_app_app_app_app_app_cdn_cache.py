"""CDN cache manager — purge, warm, and monitor cache hit rates."""
from __future__ import annotations


class CdnCacheManager:
    def __init__(self):
        self._zones: dict[str, dict] = {}

    def add_zone(self, zone_id: str, *, domain: str) -> dict:
        self._zones[zone_id] = {"domain": domain, "hits": 0, "misses": 0,
                                 "purges": 0, "cached_paths": set()}
        return {"zone_id": zone_id, "domain": domain, "status": "active"}

    def record_request(self, zone_id: str, path: str, *, cache_hit: bool) -> dict:
        z = self._zones.get(zone_id)
        if not z:
            return {"error": "Zone not found"}
        if cache_hit:
            z["hits"] += 1
        else:
            z["misses"] += 1
        z["cached_paths"].add(path)
        return {"cache_hit": cache_hit, "path": path}

    def purge(self, zone_id: str, *, paths: list[str] | None = None) -> dict:
        z = self._zones.get(zone_id)
        if not z:
            return {"error": "Zone not found"}
        if paths:
            z["cached_paths"] -= set(paths)
            purged = len(paths)
        else:
            purged = len(z["cached_paths"])
            z["cached_paths"].clear()
        z["purges"] += 1
        return {"zone_id": zone_id, "purged_paths": purged, "total_purges": z["purges"]}

    def stats(self, zone_id: str) -> dict:
        z = self._zones.get(zone_id)
        if not z:
            return {"error": "Zone not found"}
        total = z["hits"] + z["misses"]
        hit_rate = round(z["hits"] / max(total, 1) * 100, 1)
        return {"zone_id": zone_id, "domain": z["domain"],
                "hits": z["hits"], "misses": z["misses"],
                "hit_rate": hit_rate, "hit_rate_display": f"{hit_rate}%",
                "cached_paths": len(z["cached_paths"]), "purges": z["purges"],
                "health": "good" if hit_rate >= 80 else "fair" if hit_rate >= 50 else "poor"}
