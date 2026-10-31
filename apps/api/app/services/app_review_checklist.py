"""App review checklist — structured review criteria for human reviewers."""

REVIEW_CRITERIA = [
    {"id": "manifest", "label": "Manifest Valid", "category": "technical", "auto": True},
    {"id": "security", "label": "No Security Issues", "category": "security", "auto": True},
    {"id": "permissions", "label": "Permissions Justified", "category": "security", "auto": False},
    {"id": "sandbox", "label": "Sandbox Config Appropriate", "category": "technical", "auto": False},
    {"id": "description", "label": "Description Clear", "category": "quality", "auto": False},
    {"id": "branding", "label": "No Trademark Violations", "category": "legal", "auto": False},
    {"id": "privacy", "label": "Privacy Policy Provided", "category": "legal", "auto": False},
    {"id": "functionality", "label": "App Functions as Described", "category": "quality", "auto": False},
]


def create_review_checklist(*, auto_results: dict | None = None) -> list[dict]:
    """Create a checklist pre-filled with automated results."""
    checklist = []
    for criteria in REVIEW_CRITERIA:
        item = {**criteria, "checked": False, "notes": ""}
        if criteria["auto"] and auto_results:
            item["checked"] = auto_results.get(criteria["id"], {}).get("passed", False)
            item["notes"] = auto_results.get(criteria["id"], {}).get("message", "")
        checklist.append(item)
    return checklist


def is_review_complete(checklist: list[dict]) -> bool:
    return all(item["checked"] for item in checklist)


def get_review_summary(checklist: list[dict]) -> dict:
    total = len(checklist)
    checked = sum(1 for i in checklist if i["checked"])
    return {"total": total, "checked": checked, "remaining": total - checked,
            "complete": checked == total, "progress_pct": round(checked / total * 100) if total else 0}
