"""Content delivery — CDN configuration and cache management."""


CDN_REGIONS = {
    "us-east": "US East (Virginia)", "us-west": "US West (Oregon)",
    "eu-west": "Europe (Ireland)", "eu-central": "Europe (Frankfurt)",
    "ap-east": "Asia Pacific (Tokyo)", "ap-south": "Asia Pacific (Singapore)",
}


def configure_cdn(*, app_id: str, regions: list[str],
                    cache_ttl_sec: int = 3600) -> dict:
    valid = [r for r in regions if r in CDN_REGIONS]
    invalid = [r for r in regions if r not in CDN_REGIONS]
    if not valid:
        return {"error": "No valid regions specified"}
    return {
        "app_id": app_id,
        "regions": [{"id": r, "name": CDN_REGIONS[r]} for r in valid],
        "invalid_regions": invalid,
        "cache_ttl_sec": cache_ttl_sec,
        "estimated_latency_ms": {r: 20 + i * 5 for i, r in enumerate(valid)},
        "status": "active",
    }


def purge_cache(*, app_id: str, paths: list[str] | None = None) -> dict:
    return {
        "app_id": app_id,
        "purge_type": "selective" if paths else "full",
        "paths_purged": paths or ["/*"],
        "estimated_propagation_sec": 30,
        "status": "in_progress",
    }


def get_cdn_stats(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "cache_hit_rate": 94.5,
        "bandwidth_gb": 128.5,
        "requests_total": 2_500_000,
        "avg_latency_ms": 22,
        "top_paths": ["/assets/app.js", "/api/config", "/images/logo.png"],
    }
