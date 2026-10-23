"""Pill selector — multi-select pill/chip component data."""


def build_pill_selector(*, options: list[dict], selected: list[str],
                          max_select: int | None = None) -> dict:
    pills = []
    for opt in options:
        pills.append({
            "id": opt["id"],
            "label": opt["label"],
            "icon": opt.get("icon"),
            "selected": opt["id"] in selected,
            "disabled": max_select is not None and len(selected) >= max_select and opt["id"] not in selected,
        })
    return {
        "pills": pills,
        "selected_count": sum(1 for p in pills if p["selected"]),
        "total_options": len(pills),
        "max_select": max_select,
        "can_select_more": max_select is None or len(selected) < max_select,
    }
