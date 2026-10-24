"""Deployment verification — verify deployment success via smoke tests."""
from __future__ import annotations


def verify_deployment(checks: list[dict]) -> dict:
    results = []
    for c in checks:
        ok = c.get("status") == "pass"
        results.append({"check": c["name"], "status": "pass" if ok else "fail",
                        "duration_ms": c.get("duration_ms", 0),
                        "message": c.get("message", "")})
    passed = sum(1 for r in results if r["status"] == "pass")
    total = len(results)
    success = passed == total
    return {"success": success, "passed": passed, "failed": total - passed,
            "total": total, "checks": results,
            "verdict": "deploy_verified" if success else "verification_failed"}
