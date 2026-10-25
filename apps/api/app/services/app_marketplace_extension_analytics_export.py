"""Analytics Export — export extension analytics data in multiple formats.

Supports exporting usage, revenue, and engagement metrics as CSV,
JSON, and summary reports for developer dashboards.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import json


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    SUMMARY = "summary"


@dataclass
class AnalyticsRecord:
    date: str
    installs: int = 0
    uninstalls: int = 0
    api_calls: int = 0
    revenue_cents: int = 0
    active_users: int = 0
    errors: int = 0


class AnalyticsExporter:
    """Exports analytics data in multiple formats."""

    def __init__(self):
        self._data: dict[str, list[AnalyticsRecord]] = {}

    def add_records(self, extension_id: str, records: list[AnalyticsRecord]) -> None:
        self._data.setdefault(extension_id, []).extend(records)

    def export(self, extension_id: str, fmt: ExportFormat,
               date_from: str = "", date_to: str = "") -> str:
        """Export analytics data in the specified format."""
        records = self._data.get(extension_id, [])
        if date_from:
            records = [r for r in records if r.date >= date_from]
        if date_to:
            records = [r for r in records if r.date <= date_to]

        if fmt == ExportFormat.JSON:
            return self._to_json(records)
        elif fmt == ExportFormat.CSV:
            return self._to_csv(records)
        elif fmt == ExportFormat.SUMMARY:
            return self._to_summary(extension_id, records)
        return ""

    def _to_json(self, records: list[AnalyticsRecord]) -> str:
        return json.dumps([{
            "date": r.date, "installs": r.installs, "uninstalls": r.uninstalls,
            "api_calls": r.api_calls, "revenue_cents": r.revenue_cents,
            "active_users": r.active_users, "errors": r.errors,
        } for r in records], indent=2)

    def _to_csv(self, records: list[AnalyticsRecord]) -> str:
        header = "date,installs,uninstalls,api_calls,revenue_cents,active_users,errors"
        rows = [
            f"{r.date},{r.installs},{r.uninstalls},{r.api_calls},{r.revenue_cents},{r.active_users},{r.errors}"
            for r in records
        ]
        return "\n".join([header] + rows)

    def _to_summary(self, ext_id: str, records: list[AnalyticsRecord]) -> str:
        if not records:
            return f"No data for {ext_id}"
        total_installs = sum(r.installs for r in records)
        total_uninstalls = sum(r.uninstalls for r in records)
        total_revenue = sum(r.revenue_cents for r in records)
        total_api = sum(r.api_calls for r in records)
        total_errors = sum(r.errors for r in records)
        avg_active = sum(r.active_users for r in records) // len(records)
        return (
            f"Extension: {ext_id}\n"
            f"Period: {records[0].date} to {records[-1].date}\n"
            f"Days: {len(records)}\n"
            f"Installs: {total_installs} | Uninstalls: {total_uninstalls} | Net: {total_installs - total_uninstalls}\n"
            f"API Calls: {total_api} | Errors: {total_errors}\n"
            f"Revenue: ${total_revenue / 100:.2f}\n"
            f"Avg Daily Active Users: {avg_active}"
        )
