"""Analytics export — CSV/JSON export of app analytics data."""

import csv
import io
import json


def export_to_csv(*, data: list[dict], columns: list[str]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()


def export_to_json(*, data: list[dict], pretty: bool = False) -> str:
    return json.dumps({"data": data, "count": len(data)}, indent=2 if pretty else None, default=str)


def build_export_metadata(*, app_id: str, export_type: str, row_count: int, columns: list[str]) -> dict:
    return {
        "app_id": app_id, "format": export_type, "row_count": row_count,
        "columns": columns, "size_estimate_bytes": row_count * len(columns) * 20,
    }
