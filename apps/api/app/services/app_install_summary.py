"""Installation summary — compute per-org install stats."""

def compute_install_summary(installations: list[dict]) -> dict:
    active = [i for i in installations if i.get("status") == "active"]
    categories = {}
    for i in active:
        cat = i.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    return {"total": len(installations), "active": len(active), "by_category": categories}
