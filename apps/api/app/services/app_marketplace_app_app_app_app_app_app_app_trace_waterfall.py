"""Request tracing waterfall — build waterfall diagrams from trace data."""
from __future__ import annotations


def build_waterfall(spans: list[dict]) -> dict:
    sorted_spans = sorted(spans, key=lambda s: s.get("start_ms", 0))
    if not sorted_spans:
        return {"spans": [], "total_ms": 0, "depth": 0}
    min_start = sorted_spans[0]["start_ms"]
    max_end = max(s["start_ms"] + s["duration_ms"] for s in sorted_spans)
    total_ms = round(max_end - min_start, 1)
    waterfall = []
    for s in sorted_spans:
        offset_pct = round((s["start_ms"] - min_start) / max(total_ms, 0.01) * 100, 1)
        width_pct = round(s["duration_ms"] / max(total_ms, 0.01) * 100, 1)
        depth = s.get("depth", 0)
        waterfall.append({"service": s["service"], "operation": s.get("operation", ""),
                          "duration_ms": s["duration_ms"], "offset_pct": offset_pct,
                          "width_pct": width_pct, "depth": depth})
    max_depth = max(s["depth"] for s in waterfall) if waterfall else 0
    return {"spans": waterfall, "total_ms": total_ms, "depth": max_depth,
            "span_count": len(waterfall)}
