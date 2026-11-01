"""Dropdown menu — configurable dropdown menu items."""


def build_dropdown_menu(*, items: list[dict], user_role: str = "developer") -> dict:
    visible = []
    for item in items:
        roles = item.get("roles", ["developer", "admin", "viewer"])
        if user_role in roles:
            visible.append({
                "id": item["id"],
                "label": item["label"],
                "icon": item.get("icon"),
                "danger": item.get("danger", False),
                "separator_before": item.get("separator_before", False),
                "disabled": item.get("disabled", False),
            })
    return {"items": visible, "total": len(visible)}
