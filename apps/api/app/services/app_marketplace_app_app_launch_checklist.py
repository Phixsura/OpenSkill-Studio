"""App launch checklist — pre-launch readiness verification."""


LAUNCH_ITEMS = [
    {"id": "branding", "label": "App icon and screenshots ready", "category": "design"},
    {"id": "description", "label": "Compelling description written", "category": "content"},
    {"id": "pricing", "label": "Pricing strategy set", "category": "business"},
    {"id": "docs", "label": "Documentation published", "category": "content"},
    {"id": "testing", "label": "QA testing complete", "category": "engineering"},
    {"id": "security", "label": "Security review passed", "category": "engineering"},
    {"id": "performance", "label": "Performance benchmarks met", "category": "engineering"},
    {"id": "legal", "label": "Terms and privacy policy ready", "category": "legal"},
    {"id": "support", "label": "Support channels configured", "category": "operations"},
    {"id": "analytics", "label": "Analytics and tracking set up", "category": "operations"},
]


def evaluate_launch_readiness(*, completed: list[str]) -> dict:
    items = [{"completed": item["id"] in completed, **item} for item in LAUNCH_ITEMS]
    done = sum(1 for i in items if i["completed"])
    by_cat: dict[str, dict] = {}
    for item in items:
        cat = item["category"]
        if cat not in by_cat:
            by_cat[cat] = {"total": 0, "done": 0}
        by_cat[cat]["total"] += 1
        if item["completed"]:
            by_cat[cat]["done"] += 1
    categories = [{"category": k, **v, "pct": round(v["done"] / v["total"] * 100)}
                   for k, v in sorted(by_cat.items())]
    return {
        "items": items,
        "completed": done,
        "total": len(items),
        "readiness_pct": round(done / len(items) * 100),
        "launch_ready": done == len(items),
        "categories": categories,
    }
