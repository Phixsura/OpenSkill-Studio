"""Compliance report generator — generate compliance reports from checks."""
from __future__ import annotations


def generate_report(checks: list[dict], framework: str = "SOC2") -> dict:
    passed = [c for c in checks if c.get("status") == "pass"]
    failed = [c for c in checks if c.get("status") == "fail"]
    na = [c for c in checks if c.get("status") == "n/a"]
    score = round(len(passed) / max(len(passed) + len(failed), 1) * 100, 1)
    compliant = len(failed) == 0
    return {"framework": framework, "total_checks": len(checks),
            "passed": len(passed), "failed": len(failed), "na": len(na),
            "score": score, "compliant": compliant,
            "failed_checks": [{"control": c["control"], "finding": c.get("finding", "")}
                               for c in failed]}


def multi_framework(reports: list[dict]) -> dict:
    all_compliant = all(r["compliant"] for r in reports)
    avg_score = round(sum(r["score"] for r in reports) / max(len(reports), 1), 1)
    return {"frameworks": len(reports), "all_compliant": all_compliant,
            "avg_score": avg_score,
            "summary": [{"framework": r["framework"], "score": r["score"],
                          "compliant": r["compliant"]} for r in reports]}
