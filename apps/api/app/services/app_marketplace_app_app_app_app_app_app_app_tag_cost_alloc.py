"""Tag-based cost allocator — break down cloud costs by team/project tags."""
from __future__ import annotations


def allocate_by_tags(resources: list[dict], *, tag_key: str = "team") -> dict:
    by_tag: dict[str, dict] = {}
    untagged_cost = 0.0
    total = 0.0
    for r in resources:
        cost = r.get("cost", 0)
        total += cost
        tag_val = r.get("tags", {}).get(tag_key)
        if tag_val:
            if tag_val not in by_tag:
                by_tag[tag_val] = {"cost": 0, "resources": 0}
            by_tag[tag_val]["cost"] += cost
            by_tag[tag_val]["resources"] += 1
        else:
            untagged_cost += cost
    breakdown = sorted([
        {"tag": k, "cost": round(v["cost"], 2), "resources": v["resources"],
         "pct": round(v["cost"] / max(total, 0.01) * 100, 1),
         "display": f"${v['cost']:,.2f}"}
        for k, v in by_tag.items()
    ], key=lambda x: -x["cost"])
    return {
        "tag_key": tag_key, "total_cost": round(total, 2),
        "total_display": f"${total:,.2f}",
        "breakdown": breakdown, "group_count": len(breakdown),
        "untagged_cost": round(untagged_cost, 2),
        "untagged_pct": round(untagged_cost / max(total, 0.01) * 100, 1),
        "coverage_pct": round((total - untagged_cost) / max(total, 0.01) * 100, 1),
    }
