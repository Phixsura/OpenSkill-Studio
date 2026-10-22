"""Diagnostics — comprehensive health check for all app subsystems."""


def run_diagnostics(*, app_id: str, checks: dict[str, bool]) -> dict:
    results = []
    for name, passed in checks.items():
        results.append({"check": name, "status": "pass" if passed else "fail"})
    passed_count = sum(1 for r in results if r["status"] == "pass")
    return {
        "app_id": app_id, "total": len(results), "passed": passed_count,
        "failed": len(results) - passed_count,
        "health": "healthy" if passed_count == len(results) else "unhealthy",
        "results": results,
    }


def get_standard_checks() -> list[str]:
    return ["manifest_valid", "endpoints_reachable", "auth_configured",
            "webhooks_active", "secrets_rotated", "logs_flowing",
            "error_rate_normal", "response_time_normal"]
