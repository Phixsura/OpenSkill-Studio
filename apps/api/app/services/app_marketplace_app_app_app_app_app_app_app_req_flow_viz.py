"""Request flow visualizer — build visual request flow diagrams."""
from __future__ import annotations


def build_flow(steps: list[dict]) -> dict:
    nodes = []
    edges = []
    for i, step in enumerate(steps):
        nodes.append({"id": f"s{i}", "label": step["service"],
                       "operation": step.get("operation", ""),
                       "duration_ms": step.get("duration_ms", 0)})
        if i > 0:
            edges.append({"from": f"s{i-1}", "to": f"s{i}",
                          "label": step.get("protocol", "HTTP")})
    total_ms = sum(s.get("duration_ms", 0) for s in steps)
    return {"nodes": nodes, "edges": edges, "total_ms": round(total_ms, 1),
            "depth": len(steps)}


def flow_critical_path(steps: list[dict]) -> dict:
    sorted_by_dur = sorted(steps, key=lambda s: -s.get("duration_ms", 0))
    bottleneck = sorted_by_dur[0] if sorted_by_dur else None
    return {"bottleneck": bottleneck.get("service", "") if bottleneck else "",
            "bottleneck_ms": bottleneck.get("duration_ms", 0) if bottleneck else 0,
            "total_steps": len(steps)}
