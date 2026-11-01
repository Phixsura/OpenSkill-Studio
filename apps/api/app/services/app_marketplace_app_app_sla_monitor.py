"""SLA monitor — service level agreement compliance tracker."""

from datetime import datetime, timezone


def check_sla(*, metric: str, target: float, actual: float, lower_is_better: bool = False) -> dict:
    if lower_is_better:
        met = actual <= target
        margin = round(target - actual, 3)
    else:
        met = actual >= target
        margin = round(actual - target, 3)
    return {"metric": metric, "target": target, "actual": actual,
            "met": met, "margin": margin, "status": "pass" if met else "fail"}


def build_sla_report(*, checks: list[dict]) -> dict:
    results = [check_sla(**c) for c in checks]
    passed = sum(1 for r in results if r["met"])
    compliance = round(passed / max(len(results), 1) * 100, 1)
    return {"results": results, "total": len(results), "passed": passed,
            "failed": len(results) - passed, "compliance_pct": compliance,
            "overall": "compliant" if compliance == 100 else "non-compliant",
            "timestamp": datetime.now(timezone.utc).isoformat()}
