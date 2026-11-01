"""Accessibility checker — verify app UI extensions meet WCAG standards."""

WCAG_CHECKS = [
    {"id": "color-contrast", "label": "Color contrast ratio ≥ 4.5:1", "level": "AA"},
    {"id": "alt-text", "label": "Images have alt text", "level": "A"},
    {"id": "keyboard-nav", "label": "Keyboard navigation works", "level": "A"},
    {"id": "focus-visible", "label": "Focus indicators visible", "level": "AA"},
    {"id": "aria-labels", "label": "ARIA labels on interactive elements", "level": "A"},
    {"id": "heading-hierarchy", "label": "Proper heading hierarchy", "level": "A"},
    {"id": "form-labels", "label": "Form inputs have labels", "level": "A"},
    {"id": "error-messages", "label": "Error messages are descriptive", "level": "AA"},
]

def run_accessibility_audit(*, passed_checks: list[str]) -> dict:
    results = [{**c, "passed": c["id"] in passed_checks} for c in WCAG_CHECKS]
    passed = sum(1 for r in results if r["passed"])
    level_a = [r for r in results if r["level"] == "A"]
    level_a_pass = all(r["passed"] for r in level_a)
    return {"results": results, "passed": passed, "total": len(results),
            "score": round(passed / len(results) * 100),
            "wcag_a_compliant": level_a_pass, "wcag_aa_compliant": passed == len(results)}
