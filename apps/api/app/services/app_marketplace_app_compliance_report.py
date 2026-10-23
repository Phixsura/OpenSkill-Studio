"""Compliance report — generate SOC2/GDPR compliance reports for apps."""

from datetime import datetime, timezone


def generate_compliance_report(*, app_id: str, framework: str, controls: list[dict]) -> dict:
    valid_frameworks = {"soc2", "gdpr", "hipaa", "iso27001"}
    if framework not in valid_frameworks:
        return {"error": f"Unsupported framework: {framework}"}
    passed = sum(1 for c in controls if c.get("status") == "pass")
    return {
        "app_id": app_id, "framework": framework,
        "controls_checked": len(controls), "controls_passed": passed,
        "compliance_pct": round(passed / max(len(controls), 1) * 100, 1),
        "compliant": passed == len(controls),
        "generated_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def get_framework_controls(*, framework: str) -> list[dict]:
    controls = {
        "soc2": [{"id": "CC1.1", "name": "Access Control"}, {"id": "CC6.1", "name": "Encryption"},
                  {"id": "CC7.1", "name": "Monitoring"}, {"id": "CC8.1", "name": "Change Management"}],
        "gdpr": [{"id": "A5", "name": "Data Protection"}, {"id": "A6", "name": "Consent"},
                  {"id": "A17", "name": "Right to Erasure"}, {"id": "A32", "name": "Security"}],
    }
    return controls.get(framework, [])
