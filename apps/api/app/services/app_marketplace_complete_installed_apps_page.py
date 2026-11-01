"""Complete installed apps page — user's installed apps with management."""


def build_installed_apps_page(*, installations: list[dict], categories: list[str]) -> dict:
    active = [i for i in installations if i.get("status") == "active"]
    by_category = {}
    for i in active:
        cat = i.get("category", "other")
        by_category.setdefault(cat, []).append(i)
    update_available = sum(1 for i in active if i.get("update_available"))
    return {
        "page_type": "installed_apps",
        "installations": active,
        "stats": {"total": len(active), "update_available": update_available,
                   "categories_used": len(by_category)},
        "by_category": by_category,
        "filter_options": ["all"] + sorted(by_category.keys()),
        "sort_options": ["recent", "name", "category"],
        "bulk_actions": ["update_all", "uninstall_selected"],
    }
