"""Compliance report generator — create audit-ready compliance reports."""
from __future__ import annotations
import html


def generate_compliance_report(*, framework: str, org_name: str, period: str,
                                 controls: list[dict], evidence: list[dict] | None = None) -> dict:
    safe_org = html.escape(org_name)
    total = len(controls)
    passed = sum(1 for c in controls if c.get("status") == "passed")
    failed = sum(1 for c in controls if c.get("status") == "failed")
    na = sum(1 for c in controls if c.get("status") == "n/a")
    score = round(passed / max(total - na, 1) * 100)
    sections: dict[str, list[dict]] = {}
    for c in controls:
        cat = c.get("category", "General")
        sections.setdefault(cat, []).append({
            "id": c.get("id", ""), "name": c.get("name", ""),
            "status": c.get("status", "pending"), "notes": c.get("notes", ""),
        })
    return {
        "framework": framework.upper(), "organization": safe_org, "period": period,
        "total_controls": total, "passed": passed, "failed": failed, "not_applicable": na,
        "compliance_score": score, "score_display": f"{score}%",
        "verdict": "compliant" if failed == 0 else "non_compliant",
        "sections": [{"category": k, "controls": v, "count": len(v)}
                      for k, v in sections.items()],
        "evidence_count": len(evidence) if evidence else 0,
    }
