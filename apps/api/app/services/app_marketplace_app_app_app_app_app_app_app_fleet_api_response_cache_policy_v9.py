"""Fleet API Response Cache Policy v9 — track response caching rules."""
from __future__ import annotations
def fleet_api_response_cache_policy_v9(policies: list[dict]) -> dict:
    enabled = [p for p in policies if p.get("enabled")]
    hit_rate = sum(p.get("hit_rate_pct", 0) for p in policies) / len(policies) if policies else 0
    bytes_saved = sum(p.get("bytes_saved_mb", 0) for p in policies)
    return {"policies": len(policies), "enabled": len(enabled), "avg_hit_rate": round(hit_rate, 1),
            "bytes_saved_mb": round(bytes_saved, 1), "healthy": hit_rate > 70}
