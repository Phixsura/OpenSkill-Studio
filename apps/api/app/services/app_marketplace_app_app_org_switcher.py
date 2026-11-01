"""Org switcher — organization context switcher."""

import html


def build_org_switcher(*, orgs: list[dict], current_org_id: str) -> dict:
    items = []
    current = None
    for o in orgs:
        entry = {
            "id": o["id"], "name": html.escape(o.get("name", "")),
            "avatar": o.get("avatar"), "role": o.get("role", "member"),
            "plan": o.get("plan", "free"), "is_current": o["id"] == current_org_id,
            "initials": "".join(w[0].upper() for w in o.get("name", "?").split()[:2]),
        }
        if entry["is_current"]:
            current = entry
        items.append(entry)
    return {"orgs": items, "current": current, "total": len(items),
            "can_create": len(items) < 10}
