"""Compliance checker — verify app meets regulatory requirements."""


COMPLIANCE_RULES = {
    "gdpr": [
        {"id": "gdpr_privacy", "label": "Privacy policy URL provided", "required": True},
        {"id": "gdpr_data_export", "label": "User data export supported", "required": True},
        {"id": "gdpr_data_delete", "label": "User data deletion supported", "required": True},
        {"id": "gdpr_consent", "label": "Cookie consent mechanism", "required": True},
    ],
    "ccpa": [
        {"id": "ccpa_notice", "label": "Notice at collection", "required": True},
        {"id": "ccpa_opt_out", "label": "Opt-out of data sale", "required": True},
    ],
    "accessibility": [
        {"id": "a11y_alt_text", "label": "Images have alt text", "required": True},
        {"id": "a11y_keyboard", "label": "Keyboard navigation support", "required": True},
        {"id": "a11y_contrast", "label": "Color contrast ratio ≥ 4.5:1", "required": False},
    ],
}


def check_compliance(*, framework: str, app_features: dict) -> dict:
    rules = COMPLIANCE_RULES.get(framework)
    if not rules:
        return {"error": f"Unknown framework: {framework}. Available: {', '.join(COMPLIANCE_RULES)}"}
    results = []
    for rule in rules:
        met = app_features.get(rule["id"], False)
        results.append({**rule, "met": met, "status": "pass" if met else ("fail" if rule["required"] else "warning")})
    required_met = all(r["met"] for r in results if r["required"])
    return {
        "framework": framework,
        "compliant": required_met,
        "results": results,
        "passed": sum(1 for r in results if r["met"]),
        "total": len(results),
        "score": round(sum(1 for r in results if r["met"]) / len(results) * 100),
    }
