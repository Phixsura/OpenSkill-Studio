"""Developer analytics export — export analytics data in various formats."""

import json
import csv
import io


def export_as_json(data: list[dict]) -> str:
    return json.dumps(data, indent=2, default=str)


def export_as_csv(data: list[dict]) -> str:
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def build_analytics_export(*, app_name: str, period: str, metrics: list[dict]) -> dict:
    return {
        "app_name": app_name,
        "period": period,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "row_count": len(metrics),
        "json": export_as_json(metrics),
        "csv": export_as_csv(metrics),
    }
