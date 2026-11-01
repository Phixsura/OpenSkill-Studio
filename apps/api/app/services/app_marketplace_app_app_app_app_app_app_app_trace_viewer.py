"""Trace viewer — build distributed trace trees."""
from __future__ import annotations


def build_trace_tree(spans: list[dict]) -> dict:
    by_id = {s["span_id"]: s for s in spans}
    children: dict[str, list[str]] = {}
    root = None
    for s in spans:
        pid = s.get("parent_id")
        if pid:
            children.setdefault(pid, []).append(s["span_id"])
        else:
            root = s["span_id"]
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    critical_path = max(spans, key=lambda s: s.get("duration_ms", 0)) if spans else None
    return {"trace_id": spans[0].get("trace_id", "") if spans else "",
            "root_span": root, "span_count": len(spans),
            "total_duration_ms": round(total_ms, 2),
            "critical_span": critical_path["operation"] if critical_path else None,
            "depth": _tree_depth(root, children) if root else 0}


def _tree_depth(node: str, children: dict[str, list[str]]) -> int:
    kids = children.get(node, [])
    if not kids:
        return 1
    return 1 + max(_tree_depth(k, children) for k in kids)


def find_slow_spans(spans: list[dict], threshold_ms: float = 100) -> list[dict]:
    return sorted([s for s in spans if s.get("duration_ms", 0) >= threshold_ms],
                  key=lambda s: -s.get("duration_ms", 0))
