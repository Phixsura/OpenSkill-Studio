"""App publish page — complete publish flow with all checks."""

import html

PUBLISH_STEPS = [
    {"id": "manifest", "label": "Valid Manifest", "auto": True},
    {"id": "tests", "label": "Tests Passing", "auto": True},
    {"id": "security", "label": "Security Scan", "auto": True},
    {"id": "screenshots", "label": "2+ Screenshots", "auto": True},
    {"id": "description", "label": "Description (10+ chars)", "auto": True},
    {"id": "privacy", "label": "Privacy Policy", "auto": True},
    {"id": "changelog", "label": "Changelog Entry", "auto": False},
    {"id": "review", "label": "Self Review", "auto": False},
]


def build_publish_page(*, app: dict, check_results: dict[str, bool],
                          version: str, release_notes: str = "") -> dict:
    steps = []
    passed = 0
    for s in PUBLISH_STEPS:
        is_pass = check_results.get(s["id"], False)
        if is_pass:
            passed += 1
        steps.append({**s, "pass": is_pass,
                       "icon": "✅" if is_pass else "❌" if s["auto"] else "⏳"})
    can_publish = passed == len(PUBLISH_STEPS)
    score = round(passed / len(PUBLISH_STEPS) * 100)
    return {
        "app_name": html.escape(app.get("name", "")),
        "version": version,
        "release_notes": html.escape(release_notes),
        "steps": steps, "passed": passed, "total": len(PUBLISH_STEPS),
        "score": score, "can_publish": can_publish,
        "cta": "🚀 Publish to Marketplace" if can_publish else f"Complete {len(PUBLISH_STEPS) - passed} remaining checks",
    }
