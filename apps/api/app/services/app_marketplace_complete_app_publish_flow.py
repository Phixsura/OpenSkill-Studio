"""Complete app publish flow — guided publishing with review preparation."""


def build_publish_flow(*, app: dict, version: dict, checklist: list[dict],
                          manifest_valid: bool, security_clean: bool,
                          tests_passed: bool) -> dict:
    checks = [
        {"key": "manifest", "label": "Valid Manifest", "passed": manifest_valid, "required": True},
        {"key": "security", "label": "Security Scan Clean", "passed": security_clean, "required": True},
        {"key": "tests", "label": "All Tests Passed", "passed": tests_passed, "required": True},
    ] + [{"key": c["key"], "label": c["label"], "passed": c.get("passed", False),
          "required": c.get("required", False)} for c in checklist]
    all_required_passed = all(c["passed"] for c in checks if c["required"])
    passed_count = sum(1 for c in checks if c["passed"])
    return {
        "page_type": "publish_flow",
        "app": {"id": app["id"], "name": app["name"]},
        "version": version.get("version"),
        "checks": checks,
        "stats": {"passed": passed_count, "total": len(checks),
                   "pct": round(passed_count / max(len(checks), 1) * 100)},
        "ready_to_publish": all_required_passed,
        "submit_label": "Submit for Review" if all_required_passed else "Complete Required Checks",
    }
