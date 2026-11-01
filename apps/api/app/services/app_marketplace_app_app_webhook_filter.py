"""Webhook filter — event filtering rules for webhook subscriptions."""

import re
import html


def match_event(*, event_type: str, filters: list[dict]) -> dict:
    if not filters:
        return {"matched": True, "reason": "no_filters"}
    for f in filters:
        pattern = f.get("pattern", "")
        mode = f.get("mode", "exact")
        if mode == "exact" and event_type == pattern:
            return {"matched": True, "rule": f, "reason": "exact_match"}
        elif mode == "prefix" and event_type.startswith(pattern):
            return {"matched": True, "rule": f, "reason": "prefix_match"}
        elif mode == "regex":
            try:
                if re.match(pattern, event_type):
                    return {"matched": True, "rule": f, "reason": "regex_match"}
            except re.error:
                continue
    return {"matched": False, "reason": "no_matching_rule"}


def build_filter_summary(*, filters: list[dict], test_events: list[str] | None = None) -> dict:
    items = [{"pattern": html.escape(f.get("pattern", "")), "mode": f.get("mode", "exact"),
              "description": html.escape(f.get("description", ""))} for f in filters]
    results = None
    if test_events:
        results = []
        for evt in test_events:
            r = match_event(event_type=evt, filters=filters)
            results.append({"event": evt, "matched": r["matched"], "reason": r["reason"]})
    return {"filters": items, "total": len(items), "test_results": results}
