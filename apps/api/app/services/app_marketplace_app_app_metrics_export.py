"""App metrics export — export metrics in Prometheus/OpenMetrics format."""


def export_prometheus(*, metrics: list[dict]) -> dict:
    lines = []
    for m in metrics:
        name = m["name"].replace(".", "_").replace("-", "_")
        help_text = m.get("help", "")
        metric_type = m.get("type", "gauge")
        lines.append(f"# HELP {name} {help_text}")
        lines.append(f"# TYPE {name} {metric_type}")
        labels = m.get("labels", {})
        label_str = ""
        if labels:
            label_parts = ",".join(f'{k}="{v}"' for k, v in labels.items())
            label_str = f"{{{label_parts}}}"
        lines.append(f"{name}{label_str} {m['value']}")
    return {
        "content": "\n".join(lines),
        "content_type": "text/plain; version=0.0.4; charset=utf-8",
        "metric_count": len(metrics),
    }


def build_dashboard_metrics(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "metrics": [
            {"name": "app.requests.total", "value": 150000, "type": "counter",
             "help": "Total HTTP requests", "labels": {"app": app_id}},
            {"name": "app.latency.p99", "value": 0.250, "type": "gauge",
             "help": "P99 latency in seconds", "labels": {"app": app_id}},
            {"name": "app.errors.total", "value": 42, "type": "counter",
             "help": "Total errors", "labels": {"app": app_id}},
            {"name": "app.active.connections", "value": 85, "type": "gauge",
             "help": "Active connections", "labels": {"app": app_id}},
        ],
    }
