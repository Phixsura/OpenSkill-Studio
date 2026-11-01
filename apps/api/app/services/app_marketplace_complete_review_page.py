"""Complete review page — master aggregator for app review submission flow."""


def build_complete_review_page(*, app: dict, version: dict, manifest: dict,
                                  security_scan: dict, test_results: dict,
                                  checklist: list[dict]) -> dict:
    all_checks_passed = all(c.get("passed") for c in checklist)
    scan_clean = security_scan.get("vulnerabilities", 0) == 0
    tests_pass = test_results.get("pass_rate", 0) == 100
    ready = all_checks_passed and scan_clean and tests_pass
    return {
        "page_type": "review_submission",
        "app": {"id": app["id"], "name": app["name"]},
        "version": {"id": version["id"], "version": version["version"]},
        "sections": [
            {"key": "manifest", "title": "Manifest", "status": "valid" if manifest.get("valid") else "invalid"},
            {"key": "security", "title": "Security Scan", "status": "clean" if scan_clean else "issues_found",
             "data": security_scan},
            {"key": "tests", "title": "Test Results", "status": "passed" if tests_pass else "failed",
             "data": test_results},
            {"key": "checklist", "title": "Review Checklist", "items": checklist},
        ],
        "ready_to_submit": ready,
    }
