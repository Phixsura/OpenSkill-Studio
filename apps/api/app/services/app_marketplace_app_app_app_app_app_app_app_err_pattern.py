"""Error pattern detector — detect recurring error patterns."""
from __future__ import annotations
from collections import defaultdict


def detect_patterns(errors: list[dict], min_occurrences: int = 3) -> dict:
    by_pattern: dict[str, dict] = defaultdict(lambda: {"count": 0, "services": set(), "sample": ""})
    for e in errors:
        key = e.get("error_type", "unknown")
        by_pattern[key]["count"] += 1
        by_pattern[key]["services"].add(e.get("service", ""))
        if not by_pattern[key]["sample"]:
            by_pattern[key]["sample"] = e.get("message", "")[:100]
    patterns = []
    for key, data in sorted(by_pattern.items(), key=lambda x: -x[1]["count"]):
        if data["count"] >= min_occurrences:
            patterns.append({"pattern": key, "count": data["count"],
                              "services": sorted(data["services"]),
                              "sample": data["sample"]})
    return {"patterns": patterns, "total_errors": len(errors),
            "unique_patterns": len(patterns)}
