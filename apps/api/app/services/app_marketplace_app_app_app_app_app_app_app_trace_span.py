"""Distributed tracing span collector — collect and analyze trace spans."""
from __future__ import annotations


def collect_spans(spans: list[dict]) -> dict:
    by_service: dict[str, list[dict]] = {}
    for s in spans:
        svc = s.get("service", "unknown")
        by_service.setdefault(svc, []).append(s)
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    root = [s for s in spans if not s.get("parent_id")]
    return {"total_spans": len(spans), "services": len(by_service),
            "total_duration_ms": round(total_ms, 1),
            "root_spans": len(root),
            "by_service": {k: len(v) for k, v in by_service.items()}}


def find_bottleneck(spans: list[dict]) -> dict | None:
    if not spans:
        return None
    slowest = max(spans, key=lambda s: s.get("duration_ms", 0))
    return {"span_id": slowest.get("span_id", ""),
            "service": slowest.get("service", ""),
            "operation": slowest.get("operation", ""),
            "duration_ms": slowest.get("duration_ms", 0)}


def trace_depth(spans: list[dict]) -> int:
    children: dict[str, list[str]] = {}
    roots = []
    for s in spans:
        pid = s.get("parent_id")
        sid = s.get("span_id", "")
        if not pid:
            roots.append(sid)
        else:
            children.setdefault(pid, []).append(sid)
    def depth(sid: str) -> int:
        if sid not in children:
            return 1
        return 1 + max(depth(c) for c in children[sid])
    return max((depth(r) for r in roots), default=0)
