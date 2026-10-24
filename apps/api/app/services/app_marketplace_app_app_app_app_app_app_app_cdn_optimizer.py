"""CDN optimizer — optimize content delivery and cache hit rates."""
from __future__ import annotations
from collections import defaultdict


def analyze_cdn(requests: list[dict]) -> dict:
    hits = sum(1 for r in requests if r.get("cache") == "hit")
    misses = sum(1 for r in requests if r.get("cache") == "miss")
    total = len(requests)
    hit_rate = round(hits / max(total, 1) * 100, 1)
    by_region: dict[str, dict] = defaultdict(lambda: {"hits": 0, "misses": 0})
    for r in requests:
        region = r.get("region", "unknown")
        if r.get("cache") == "hit":
            by_region[region]["hits"] += 1
        else:
            by_region[region]["misses"] += 1
    regions = []
    for region, data in sorted(by_region.items()):
        total_r = data["hits"] + data["misses"]
        regions.append({"region": region, "hit_rate": round(data["hits"] / max(total_r, 1) * 100, 1),
                        "requests": total_r})
    bandwidth_saved = round(hits * 0.5, 1)  # estimate 0.5MB per cache hit
    return {"total_requests": total, "hits": hits, "misses": misses,
            "hit_rate": hit_rate, "regions": regions,
            "bandwidth_saved_mb": bandwidth_saved}
