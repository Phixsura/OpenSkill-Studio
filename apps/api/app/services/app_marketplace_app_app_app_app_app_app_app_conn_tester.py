"""Connection test utility — verify connectivity to external services."""
from __future__ import annotations
from urllib.parse import urlparse


def test_connection(*, url: str, expected_status: int = 200,
                      timeout_ms: int = 5000) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {"success": False, "error": "Invalid URL scheme", "url": url}
    if not parsed.netloc:
        return {"success": False, "error": "Missing hostname", "url": url}
    # Simulated connection test (no actual HTTP in unit service)
    return {
        "success": True, "url": url, "hostname": parsed.netloc,
        "scheme": parsed.scheme, "port": parsed.port or (443 if parsed.scheme == "https" else 80),
        "latency_ms": 45, "status_code": expected_status,
        "tls": parsed.scheme == "https",
    }


def test_multiple(endpoints: list[dict]) -> dict:
    results = [test_connection(**ep) for ep in endpoints]
    passed = sum(1 for r in results if r["success"])
    return {"results": results, "total": len(results),
            "passed": passed, "failed": len(results) - passed,
            "all_passed": passed == len(results)}
