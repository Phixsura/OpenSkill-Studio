"""Search filter — faceted search with multi-criteria filtering."""

import html


def apply_filters(*, items: list[dict], filters: dict) -> dict:
    result = list(items)
    applied = []
    for key, value in filters.items():
        if value is None or value == "":
            continue
        if isinstance(value, list):
            result = [i for i in result if i.get(key) in value]
        elif isinstance(value, dict):
            if "min" in value:
                result = [i for i in result if i.get(key, 0) >= value["min"]]
            if "max" in value:
                result = [i for i in result if i.get(key, 0) <= value["max"]]
        else:
            result = [i for i in result if str(value).lower() in str(i.get(key, "")).lower()]
        applied.append(key)
    return {"items": result, "total": len(result), "original_count": len(items),
            "filtered_out": len(items) - len(result), "applied_filters": applied}


def build_facets(*, items: list[dict], facet_fields: list[str]) -> dict:
    facets = {}
    for field in facet_fields:
        counts: dict[str, int] = {}
        for item in items:
            val = str(item.get(field, ""))
            if val:
                counts[val] = counts.get(val, 0) + 1
        facets[field] = sorted([{"value": v, "count": c} for v, c in counts.items()],
                                key=lambda x: -x["count"])
    return {"facets": facets, "field_count": len(facets)}
