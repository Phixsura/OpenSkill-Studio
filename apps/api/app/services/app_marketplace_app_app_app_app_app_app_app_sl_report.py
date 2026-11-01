"""Service level report — comprehensive SLO/SLI/SLA reporting."""
from __future__ import annotations


def generate_sl_report(slos: list[dict], period: str = "monthly") -> dict:
    results = []
    met_count = 0
    for slo in slos:
        actual = slo.get("actual_pct", 0)
        target = slo.get("target_pct", 99.9)
        met = actual >= target
        if met:
            met_count += 1
        budget_remaining = max(0, round((actual - target) / (100 - target) * 100, 1)) if target < 100 else 0
        results.append({"name": slo["name"], "actual": actual, "target": target,
                         "met": met, "budget_remaining_pct": budget_remaining})
    return {"slos": results, "total": len(slos), "met": met_count,
            "failed": len(slos) - met_count, "period": period,
            "compliance_pct": round(met_count / max(len(slos), 1) * 100)}


def executive_summary(report: dict) -> dict:
    grade = "A" if report["compliance_pct"] >= 95 else "B" if report["compliance_pct"] >= 80 else "C"
    return {"grade": grade, "compliance": report["compliance_pct"],
            "met": report["met"], "failed": report["failed"],
            "summary": f"{report['met']}/{report['total']} SLOs met ({report['compliance_pct']}%)"}
