"""Metric exporter — export metrics in Prometheus/OpenMetrics format."""
from __future__ import annotations


def export_prometheus(metrics: list[dict]) -> str:
    lines = []
    for m in metrics:
        name = m["name"]
        mtype = m.get("type", "gauge")
        lines.append(f"# HELP {name} {m.get('help', '')}")
        lines.append(f"# TYPE {name} {mtype}")
        if "labels" in m:
            label_str = ",".join(f'{k}="{v}"' for k, v in m["labels"].items())
            lines.append(f"{name}{{{label_str}}} {m['value']}")
        else:
            lines.append(f"{name} {m['value']}")
    return "\n".join(lines)


def metrics_summary(metrics: list[dict]) -> dict:
    by_type = {}
    for m in metrics:
        t = m.get("type", "gauge")
        by_type[t] = by_type.get(t, 0) + 1
    return {"total": len(metrics), "by_type": by_type,
            "with_labels": sum(1 for m in metrics if "labels" in m)}
