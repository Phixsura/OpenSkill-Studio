"""Platform metrics exporter — export metrics in Prometheus format."""
from __future__ import annotations


def export_prometheus(metrics: list[dict]) -> dict:
    lines = []
    for m in metrics:
        name = m["name"]
        mtype = m.get("type", "gauge")
        help_text = m.get("help", "")
        value = m.get("value", 0)
        labels = m.get("labels", {})
        if help_text:
            lines.append(f"# HELP {name} {help_text}")
        lines.append(f"# TYPE {name} {mtype}")
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            lines.append(f"{name}{{{label_str}}} {value}")
        else:
            lines.append(f"{name} {value}")
    text = "\n".join(lines)
    return {"text": text, "content_type": "text/plain; version=0.0.4",
            "metric_count": len(metrics), "line_count": len(lines)}


def build_platform_metrics(*, requests_total: int, errors_total: int,
                             latency_avg_ms: float, active_users: int,
                             apps_count: int) -> list[dict]:
    return [
        {"name": "platform_requests_total", "type": "counter", "value": requests_total,
         "help": "Total API requests"},
        {"name": "platform_errors_total", "type": "counter", "value": errors_total,
         "help": "Total error responses"},
        {"name": "platform_latency_avg_ms", "type": "gauge", "value": latency_avg_ms,
         "help": "Average response latency"},
        {"name": "platform_active_users", "type": "gauge", "value": active_users,
         "help": "Currently active users"},
        {"name": "platform_apps_count", "type": "gauge", "value": apps_count,
         "help": "Total registered apps"},
    ]
