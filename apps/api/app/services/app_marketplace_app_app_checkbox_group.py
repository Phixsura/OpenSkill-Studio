"""Checkbox group — configurable checkbox group for multi-select."""


def build_checkbox_group(*, name: str, label: str, options: list[dict],
                           selected: list[str], min_select: int = 0,
                           max_select: int | None = None) -> dict:
    items = []
    for opt in options:
        items.append({
            "value": opt["value"],
            "label": opt.get("label", opt["value"]),
            "checked": opt["value"] in selected,
            "disabled": opt.get("disabled", False) or (
                max_select is not None and len(selected) >= max_select and opt["value"] not in selected),
        })
    valid = min_select <= len(selected) <= (max_select or len(options))
    return {"name": name, "label": label, "items": items,
            "selected_count": len(selected), "valid": valid,
            "min_select": min_select, "max_select": max_select}
