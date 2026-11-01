"""Accessibility checker — WCAG compliance audit for UI components."""

import html
import re

CHECKS = {
    "alt_text": {"description": "Images must have alt text", "wcag": "1.1.1", "level": "A"},
    "color_contrast": {"description": "Text must have sufficient contrast", "wcag": "1.4.3", "level": "AA"},
    "focus_visible": {"description": "Focus must be visible", "wcag": "2.4.7", "level": "AA"},
    "label": {"description": "Form inputs must have labels", "wcag": "1.3.1", "level": "A"},
    "heading_order": {"description": "Headings must be in order", "wcag": "1.3.1", "level": "A"},
    "link_text": {"description": "Links must have descriptive text", "wcag": "2.4.4", "level": "A"},
    "keyboard_nav": {"description": "All interactive elements keyboard accessible", "wcag": "2.1.1", "level": "A"},
}


def run_audit(*, checks: list[dict]) -> dict:
    results = []
    passed = failed = 0
    for c in checks:
        check_id = c.get("id", "")
        check_info = CHECKS.get(check_id, {})
        is_pass = c.get("pass", True)
        if is_pass:
            passed += 1
        else:
            failed += 1
        results.append({
            "id": check_id,
            "description": check_info.get("description", ""),
            "wcag": check_info.get("wcag", ""),
            "level": check_info.get("level", ""),
            "pass": is_pass,
            "details": html.escape(c.get("details", "")),
        })
    score = round(passed / max(len(results), 1) * 100)
    return {"results": results, "passed": passed, "failed": failed,
            "total": len(results), "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 70 else "C" if score >= 50 else "F"}
