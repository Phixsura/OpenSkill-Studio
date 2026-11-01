"""Compliance report generator — generate compliance audit reports."""
from __future__ import annotations
import time
import hashlib


def generate_report(org: str, framework: str, controls: list[dict]) -> dict:
    report_id = hashlib.sha256(f"{org}:{framework}:{time.time()}".encode()).hexdigest()[:10]
    passed = sum(1 for c in controls if c.get("status") == "passed")
    failed = sum(1 for c in controls if c.get("status") == "failed")
    na = len(controls) - passed - failed
    score = round(passed / max(len(controls), 1) * 100)
    return {"report_id": report_id, "org": org, "framework": framework,
            "controls": controls, "total": len(controls),
            "passed": passed, "failed": failed, "not_applicable": na,
            "score": score, "compliant": failed == 0}


def control_summary(reports: list[dict]) -> dict:
    total_controls = sum(r["total"] for r in reports)
    total_passed = sum(r["passed"] for r in reports)
    frameworks = [r["framework"] for r in reports]
    avg_score = round(sum(r["score"] for r in reports) / max(len(reports), 1))
    return {"reports": len(reports), "frameworks": frameworks,
            "total_controls": total_controls, "total_passed": total_passed,
            "avg_score": avg_score}
