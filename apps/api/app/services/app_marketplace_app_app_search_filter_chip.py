"""Search filter chip — manage active search filters."""


FILTER_TYPES = {
    "category": {"label": "Category", "icon": "📂", "multi": False},
    "rating": {"label": "Min Rating", "icon": "⭐", "multi": False},
    "price": {"label": "Price", "icon": "💰", "multi": False},
    "platform": {"label": "Platform", "icon": "📱", "multi": True},
    "sort": {"label": "Sort By", "icon": "↕️", "multi": False},
}


def build_active_filters(*, filters: dict) -> dict:
    chips = []
    for key, value in filters.items():
        ftype = FILTER_TYPES.get(key, {"label": key.title(), "icon": "🔘", "multi": False})
        if isinstance(value, list):
            for v in value:
                chips.append({"key": key, "value": v, "label": f"{ftype['label']}: {v}", "icon": ftype["icon"]})
        else:
            chips.append({"key": key, "value": value, "label": f"{ftype['label']}: {value}", "icon": ftype["icon"]})
    return {"chips": chips, "active_count": len(chips), "has_filters": len(chips) > 0}


def remove_filter(*, filters: dict, key: str, value: str | None = None) -> dict:
    updated = dict(filters)
    if key in updated:
        if isinstance(updated[key], list) and value:
            updated[key] = [v for v in updated[key] if v != value]
            if not updated[key]:
                del updated[key]
        else:
            del updated[key]
    return {"filters": updated}
