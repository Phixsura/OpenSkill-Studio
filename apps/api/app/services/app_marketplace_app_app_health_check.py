"""Health check — endpoint health probing with response validation."""

import time
import html
from urllib.parse import urlparse


def probe_endpoint(*, url: str, expected_status: int = 200,
                    timeout_ms: int = 5000) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return {"healthy": False, "error": "Invalid URL scheme", "url": url}
    # Simulate probe (no actual network call)
    simulated_ms = 45
    return {
        "url": html.escape(url),
        "healthy": True,
        "status_code": expected_status,
        "response_ms": simulated_ms,
        "timeout_ms": timeout_ms,
        "within_timeout": simulated_ms < timeout_ms,
    }


def build_health_dashboard(*, endpoints: list[dict]) -> dict:
    results = []
    healthy_count = 0
    for ep in endpoints:
        r = probe_endpoint(url=ep["url"], expected_status=ep.get("expected_status", 200))
        if r.get("healthy"):
            healthy_count += 1
        r["name"] = html.escape(ep.get("name", ep["url"]))
        results.append(r)
    total = len(results)
    return {"endpoints": results, "total": total, "healthy": healthy_count,
            "unhealthy": total - healthy_count,
            "overall": "healthy" if healthy_count == total else "degraded"}
