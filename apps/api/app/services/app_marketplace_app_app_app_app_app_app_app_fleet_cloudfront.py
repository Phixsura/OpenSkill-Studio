"""Fleet CloudFront — track CDN distribution health."""
from __future__ import annotations
def fleet_cloudfront_status(distributions: list[dict]) -> dict:
    deployed = [d for d in distributions if d.get("status") == "Deployed"]
    total_requests = sum(d.get("requests_24h", 0) for d in distributions)
    cache_hit = round(sum(d.get("cache_hit_pct", 0) for d in distributions) / max(len(distributions), 1), 1)
    return {"distributions": len(distributions), "deployed": len(deployed), "requests_24h": total_requests,
            "cache_hit_pct": cache_hit, "all_deployed": len(deployed) == len(distributions)}
