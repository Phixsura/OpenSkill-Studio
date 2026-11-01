"""Compliance tracker — track compliance across multiple frameworks."""
from __future__ import annotations


def track_compliance(frameworks: dict[str, dict]) -> dict:
    results = {}
    total_controls = 0
    total_passed = 0
    for name, data in frameworks.items():
        passed = data.get("passed", 0)
        total = data.get("total", 0)
        total_controls += total
        total_passed += passed
        pct = round(passed / max(total, 1) * 100)
        results[name] = {"passed": passed, "total": total, "pct": pct,
                          "compliant": passed == total}
    overall = round(total_passed / max(total_controls, 1) * 100)
    all_compliant = all(r["compliant"] for r in results.values())
    return {"frameworks": results, "overall_pct": overall, "all_compliant": all_compliant,
            "total_controls": total_controls, "total_passed": total_passed}
