"""Compliance check — regulatory compliance scanner."""

import html

FRAMEWORKS = {
    "gdpr": {"name": "GDPR", "region": "EU", "checks": [
        "data_encryption", "consent_management", "right_to_delete", "data_portability", "privacy_policy"]},
    "soc2": {"name": "SOC 2", "region": "Global", "checks": [
        "access_controls", "encryption", "monitoring", "incident_response", "vendor_management"]},
    "hipaa": {"name": "HIPAA", "region": "US", "checks": [
        "phi_encryption", "access_audit", "backup_recovery", "employee_training", "baa_agreements"]},
}


def run_compliance_check(*, framework: str, results: dict[str, bool]) -> dict:
    fw = FRAMEWORKS.get(framework)
    if not fw:
        return {"error": f"Unknown framework: {framework}"}
    checks = []
    passed = 0
    for check in fw["checks"]:
        is_pass = results.get(check, False)
        if is_pass:
            passed += 1
        checks.append({"check": check, "pass": is_pass,
                        "label": check.replace("_", " ").title()})
    total = len(checks)
    score = round(passed / max(total, 1) * 100)
    return {"framework": fw["name"], "region": fw["region"],
            "checks": checks, "passed": passed, "failed": total - passed,
            "total": total, "score": score,
            "compliant": passed == total}
