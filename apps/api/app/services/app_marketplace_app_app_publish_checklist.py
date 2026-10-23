"""App publish checklist — final verification before publishing."""


CHECKLIST_ITEMS = [
    {"id": "manifest", "label": "Valid manifest.json", "category": "required", "auto_check": True},
    {"id": "icon", "label": "App icon uploaded (512x512)", "category": "required", "auto_check": True},
    {"id": "screenshots", "label": "At least 3 screenshots", "category": "required", "auto_check": True},
    {"id": "description", "label": "Description (100+ chars)", "category": "required", "auto_check": True},
    {"id": "privacy", "label": "Privacy policy URL", "category": "required", "auto_check": True},
    {"id": "tests", "label": "All tests passing", "category": "quality", "auto_check": True},
    {"id": "security", "label": "Security scan clean", "category": "quality", "auto_check": True},
    {"id": "perf", "label": "Performance budget met", "category": "quality", "auto_check": False},
    {"id": "changelog", "label": "Changelog updated", "category": "recommended", "auto_check": False},
    {"id": "docs", "label": "Documentation complete", "category": "recommended", "auto_check": False},
]


def evaluate_checklist(*, results: dict[str, bool]) -> dict:
    items = []
    for item in CHECKLIST_ITEMS:
        passed = results.get(item["id"], False)
        items.append({**item, "passed": passed})
    required_passed = all(i["passed"] for i in items if i["category"] == "required")
    quality_passed = all(i["passed"] for i in items if i["category"] == "quality")
    total_passed = sum(1 for i in items if i["passed"])
    return {
        "items": items,
        "total": len(items),
        "passed": total_passed,
        "can_publish": required_passed,
        "quality_check": quality_passed,
        "readiness_pct": round(total_passed / len(items) * 100),
        "blocking": [i["label"] for i in items if i["category"] == "required" and not i["passed"]],
    }
