"""Metrics export — export app metrics in various formats for reporting."""

import csv
import io
import json


def export_metrics_json(*, metrics: dict, app_name: str, period: str) -> str:
    return json.dumps({"app": app_name, "period": period, "metrics": metrics,
                        "exported_at": "now", "format": "json"}, indent=2, default=str)


def export_metrics_csv(*, data_points: list[dict], columns: list[str]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for dp in data_points:
        writer.writerow(dp)
    return output.getvalue()


def build_export_options(*, available_metrics: list[str]) -> list[dict]:
    return [
        {"id": "json", "label": "JSON", "icon": "📄", "mime": "application/json"},
        {"id": "csv", "label": "CSV", "icon": "📊", "mime": "text/csv"},
        {"id": "pdf", "label": "PDF Report", "icon": "📑", "mime": "application/pdf"},
    ]


def estimate_export_size(*, metric_count: int, data_points: int, format: str) -> dict:
    sizes = {"json": metric_count * data_points * 50, "csv": metric_count * data_points * 30,
             "pdf": metric_count * data_points * 100 + 50000}
    size = sizes.get(format, 0)
    return {"estimated_bytes": size, "estimated_kb": round(size / 1024, 1),
            "estimated_mb": round(size / (1024 * 1024), 2)}
