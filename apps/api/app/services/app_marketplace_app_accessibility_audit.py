"""Accessibility audit — WCAG compliance checker for apps."""


WCAG_RULES = [
    {"id": "color-contrast", "level": "AA", "description": "Text has sufficient color contrast (4.5:1)"},
    {"id": "alt-text", "level": "A", "description": "Images have descriptive alt text"},
    {"id": "keyboard-nav", "level": "A", "description": "All interactive elements reachable via keyboard"},
    {"id": "focus-visible", "level": "AA", "description": "Focus indicator is visible"},
    {"id": "heading-order", "level": "A", "description": "Headings follow logical order"},
    {"id": "aria-labels", "level": "A", "description": "ARIA labels on interactive elements"},
    {"id": "form-labels", "level": "A", "description": "Form inputs have associated labels"},
    {"id": "skip-link", "level": "AA", "description": "Skip to main content link present"},
]


def run_audit(*, results: dict[str, bool]) -> dict:
    findings = []
    for rule in WCAG_RULES:
        passed = results.get(rule["id"], False)
        findings.append({**rule, "passed": passed, "status": "pass" if passed else "fail"})
    passed_count = sum(1 for f in findings if f["passed"])
    level_a = [f for f in findings if f["level"] == "A"]
    level_aa = [f for f in findings if f["level"] == "AA"]
    a_pass = all(f["passed"] for f in level_a)
    aa_pass = a_pass and all(f["passed"] for f in level_aa)
    return {
        "findings": findings,
        "passed": passed_count,
        "total": len(findings),
        "score": round(passed_count / len(findings) * 100),
        "wcag_a_compliant": a_pass,
        "wcag_aa_compliant": aa_pass,
        "grade": "A" if aa_pass else "B" if a_pass else "C" if passed_count > len(findings) // 2 else "F",
    }
