"""Distributed tracing — trace requests across microservices."""

import secrets


def create_trace(*, trace_id: str | None = None, service: str,
                   operation: str, parent_span_id: str | None = None) -> dict:
    tid = trace_id or secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return {
        "trace_id": tid,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "service": service,
        "operation": operation,
        "status": "ok",
        "duration_ms": 0,
        "is_root": parent_span_id is None,
    }


def build_trace_tree(*, spans: list[dict]) -> dict:
    by_id = {s["span_id"]: {**s, "children": []} for s in spans}
    roots = []
    for s in spans:
        parent = s.get("parent_span_id")
        if parent and parent in by_id:
            by_id[parent]["children"].append(by_id[s["span_id"]])
        else:
            roots.append(by_id[s["span_id"]])
    total_duration = sum(s.get("duration_ms", 0) for s in spans)
    services = sorted(set(s["service"] for s in spans))
    return {
        "roots": roots,
        "total_spans": len(spans),
        "total_duration_ms": total_duration,
        "services": services,
        "depth": _tree_depth(roots),
    }


def _tree_depth(nodes: list, level: int = 1) -> int:
    if not nodes:
        return level - 1
    return max(_tree_depth(n.get("children", []), level + 1) for n in nodes)
