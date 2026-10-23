"""Accessibility score — quick accessibility assessment for apps."""


A11Y_CHECKS = [
    {"id": "alt_text", "label": "Image alt text", "weight": 15, "category": "perceivable"},
    {"id": "color_contrast", "label": "Color contrast ≥ 4.5:1", "weight": 15, "category": "perceivable"},
    {"id": "keyboard_nav", "label": "Keyboard navigation", "weight": 20, "category": "operable"},
    {"id": "focus_visible", "label": "Visible focus indicators", "weight": 10, "category": "operable"},
    {"id": "form_labels", "label": "Form input labels", "weight": 15, "category": "understandable"},
    {"id": "error_messages", "label": "Clear error messages", "weight": 10, "category": "understandable"},
    {"id": "semantic_html", "label": "Semantic HTML structure", "weight": 10, "category": "robust"},
    {"id": "aria_roles", "label": "ARIA roles and labels", "weight": 5, "category": "robust"},
]


def calculate_a11y_score(*, results: dict[str, bool]) -> dict:
    checks = []
    total_weight = sum(c["weight"] for c in A11Y_CHECKS)
    earned = 0
    for check in A11Y_CHECKS:
        passed = results.get(check["id"], False)
        if passed:
            earned += check["weight"]
        checks.append({**check, "passed": passed})
    score = round(earned / total_weight * 100)
    return {
        "score": score,
        "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 50 else "F",
        "checks": checks,
        "passed": sum(1 for c in checks if c["passed"]),
        "total": len(checks),
    }
