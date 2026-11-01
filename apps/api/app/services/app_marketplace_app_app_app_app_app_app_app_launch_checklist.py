"""App launch checklist — everything needed before going live."""
from __future__ import annotations

CHECKLIST_ITEMS = [
    {"id": "listing", "title": "Complete App Listing", "category": "listing", "required": True},
    {"id": "screenshots", "title": "Add Screenshots (3+)", "category": "listing", "required": True},
    {"id": "privacy", "title": "Privacy Policy URL", "category": "legal", "required": True},
    {"id": "tos", "title": "Terms of Service", "category": "legal", "required": False},
    {"id": "security_scan", "title": "Pass Security Scan", "category": "security", "required": True},
    {"id": "test_install", "title": "Test Installation Flow", "category": "testing", "required": True},
    {"id": "webhook_test", "title": "Test Webhook Delivery", "category": "testing", "required": False},
    {"id": "docs", "title": "API Documentation", "category": "docs", "required": True},
    {"id": "support", "title": "Support Contact Info", "category": "support", "required": True},
    {"id": "branding", "title": "Follow Branding Guidelines", "category": "branding", "required": False},
]


def evaluate_checklist(completed: list[str]) -> dict:
    results = [{"id": item["id"], "title": item["title"], "category": item["category"],
                 "required": item["required"], "completed": item["id"] in completed}
               for item in CHECKLIST_ITEMS]
    required_done = all(r["completed"] for r in results if r["required"])
    total_done = sum(1 for r in results if r["completed"])
    pct = round(total_done / len(results) * 100)
    return {"results": results, "total": len(results), "completed": total_done,
            "progress_pct": pct, "ready_to_launch": required_done,
            "missing_required": [r["title"] for r in results if r["required"] and not r["completed"]]}
