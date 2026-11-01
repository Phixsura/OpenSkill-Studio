"""Complete compliance page — compliance dashboard with audits, reports, and remediation."""


def build_complete_compliance_page(*, app: dict, audit_results: list[dict],
                                       compliance_score: int, frameworks: list[str],
                                       remediation_steps: list[dict]) -> dict:
    critical = sum(1 for r in audit_results if not r.get("passed") and r.get("severity") == "critical")
    return {
        "page_type": "compliance_dashboard",
        "app": {"id": app["id"], "name": app["name"]},
        "score": compliance_score,
        "grade": "A" if compliance_score >= 90 else "B" if compliance_score >= 75 else "C" if compliance_score >= 60 else "F",
        "frameworks": frameworks,
        "audit_results": audit_results,
        "critical_issues": critical,
        "remediation": remediation_steps,
        "compliant": critical == 0 and compliance_score >= 80,
        "tabs": [
            {"key": "overview", "title": "Overview", "icon": "📊"},
            {"key": "audit", "title": f"Audit ({len(audit_results)})", "icon": "📋"},
            {"key": "remediation", "title": f"Fix ({len(remediation_steps)})", "icon": "🔧"},
            {"key": "reports", "title": "Reports", "icon": "📄"},
        ],
    }
