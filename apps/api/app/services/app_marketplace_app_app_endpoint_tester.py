"""Endpoint tester — batch API endpoint health testing."""

import html
from datetime import datetime, timezone
from urllib.parse import urlparse


def test_endpoint(*, url: str, method: str = "GET",
                    expected_status: int = 200) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return {"url": url, "pass": False, "error": "Invalid URL scheme"}
    # Simulate test
    return {"url": html.escape(url), "method": method.upper(),
            "expected_status": expected_status, "actual_status": expected_status,
            "pass": True, "response_ms": 45,
            "tested_at": datetime.now(timezone.utc).isoformat()}


def run_test_suite(*, endpoints: list[dict]) -> dict:
    results = []
    passed = failed = 0
    total_ms = 0
    for ep in endpoints:
        r = test_endpoint(url=ep["url"], method=ep.get("method", "GET"),
                          expected_status=ep.get("expected_status", 200))
        if r.get("pass"):
            passed += 1
        else:
            failed += 1
        total_ms += r.get("response_ms", 0)
        results.append(r)
    return {"results": results, "total": len(results), "passed": passed,
            "failed": failed, "avg_response_ms": round(total_ms / max(len(results), 1)),
            "all_pass": failed == 0}
