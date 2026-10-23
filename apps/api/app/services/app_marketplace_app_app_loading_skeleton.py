"""Loading skeleton — generate loading placeholder configurations."""


SKELETON_TEMPLATES = {
    "app_card": {"rows": [
        {"type": "circle", "size": 48},
        {"type": "line", "width": "60%", "height": 16},
        {"type": "line", "width": "80%", "height": 12},
        {"type": "line", "width": "40%", "height": 12},
    ]},
    "dashboard_stats": {"rows": [
        {"type": "rect", "width": "100%", "height": 80},
        {"type": "rect", "width": "100%", "height": 80},
        {"type": "rect", "width": "100%", "height": 80},
    ], "layout": "grid", "columns": 3},
    "list_item": {"rows": [
        {"type": "line", "width": "30%", "height": 14},
        {"type": "line", "width": "70%", "height": 12},
    ]},
    "profile_header": {"rows": [
        {"type": "circle", "size": 64},
        {"type": "line", "width": "40%", "height": 20},
        {"type": "line", "width": "60%", "height": 12},
    ]},
}


def get_skeleton(*, template: str, count: int = 1) -> dict:
    tpl = SKELETON_TEMPLATES.get(template)
    if not tpl:
        return {"error": f"Unknown template. Valid: {', '.join(sorted(SKELETON_TEMPLATES))}"}
    return {"template": template, "config": tpl, "count": count,
            "row_count": len(tpl["rows"]) * count}
