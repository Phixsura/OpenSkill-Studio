"""Tracing context — distributed tracing span builder."""

import secrets
import html
from datetime import datetime, timezone


def create_trace() -> dict:
    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return {"trace_id": trace_id, "span_id": span_id,
            "traceparent": f"00-{trace_id}-{span_id}-01",
            "started_at": datetime.now(timezone.utc).isoformat()}


def create_span(*, trace_id: str, parent_span_id: str | None = None,
                  operation: str, service: str) -> dict:
    span_id = secrets.token_hex(8)
    return {"trace_id": trace_id, "span_id": span_id,
            "parent_span_id": parent_span_id,
            "operation": html.escape(operation), "service": html.escape(service),
            "status": "in_progress", "started_at": datetime.now(timezone.utc).isoformat()}


def build_trace_waterfall(*, spans: list[dict]) -> dict:
    items = sorted(spans, key=lambda s: s.get("started_at", ""))
    root = [s for s in items if not s.get("parent_span_id")]
    return {"spans": items, "total_spans": len(items),
            "services": list(set(s.get("service", "") for s in items)),
            "root_spans": len(root), "max_depth": _calc_depth(items)}


def _calc_depth(spans: list[dict]) -> int:
    children: dict[str, list] = {}
    for s in spans:
        pid = s.get("parent_span_id")
        if pid:
            children.setdefault(pid, []).append(s["span_id"])
    roots = [s["span_id"] for s in spans if not s.get("parent_span_id")]
    if not roots:
        return 0
    max_d = 0
    stack = [(r, 1) for r in roots]
    while stack:
        sid, d = stack.pop()
        max_d = max(max_d, d)
        for c in children.get(sid, []):
            stack.append((c, d + 1))
    return max_d
