"""Content policy — enforce platform content guidelines."""

import re


FORBIDDEN_CATEGORIES = {"malware", "gambling", "adult", "weapons", "hate_speech"}

NAME_BLOCKLIST = re.compile(r"(official|certified|verified)\s+(google|apple|microsoft|amazon)", re.IGNORECASE)


def check_content_policy(*, app_name: str, description: str,
                           category: str, screenshots: int = 0) -> dict:
    violations = []
    if category.lower() in FORBIDDEN_CATEGORIES:
        violations.append({"rule": "forbidden_category", "severity": "critical",
                           "detail": f"Category '{category}' is not allowed"})
    if NAME_BLOCKLIST.search(app_name):
        violations.append({"rule": "impersonation", "severity": "critical",
                           "detail": "App name implies official affiliation"})
    if len(description) < 50:
        violations.append({"rule": "min_description", "severity": "warning",
                           "detail": "Description should be at least 50 characters"})
    if screenshots < 1:
        violations.append({"rule": "min_screenshots", "severity": "warning",
                           "detail": "At least 1 screenshot is required"})
    if len(app_name) > 50:
        violations.append({"rule": "name_length", "severity": "warning",
                           "detail": "App name should be 50 characters or less"})
    passed = not any(v["severity"] == "critical" for v in violations)
    return {"passed": passed, "violations": violations,
            "critical_count": sum(1 for v in violations if v["severity"] == "critical"),
            "warning_count": sum(1 for v in violations if v["severity"] == "warning")}
