from app.services.app_marketplace_extension_analytics_export import (
    AnalyticsExporter, AnalyticsRecord, ExportFormat,
)
import json


SAMPLE = [
    AnalyticsRecord("2026-10-24", 10, 2, 5000, 999, 300, 5),
    AnalyticsRecord("2026-10-25", 15, 1, 6000, 1499, 350, 3),
    AnalyticsRecord("2026-10-26", 8, 0, 4500, 799, 280, 1),
]


def test_export_json():
    exp = AnalyticsExporter()
    exp.add_records("ext-1", SAMPLE)
    output = exp.export("ext-1", ExportFormat.JSON)
    data = json.loads(output)
    assert len(data) == 3
    assert data[0]["installs"] == 10


def test_export_csv():
    exp = AnalyticsExporter()
    exp.add_records("ext-2", SAMPLE)
    output = exp.export("ext-2", ExportFormat.CSV)
    lines = output.strip().split("\n")
    assert lines[0] == "date,installs,uninstalls,api_calls,revenue_cents,active_users,errors"
    assert len(lines) == 4  # header + 3 data rows


def test_export_summary():
    exp = AnalyticsExporter()
    exp.add_records("ext-3", SAMPLE)
    output = exp.export("ext-3", ExportFormat.SUMMARY)
    assert "ext-3" in output
    assert "Net: 30" in output  # 33 installs - 3 uninstalls
    assert "$32.97" in output
    assert "Days: 3" in output


def test_date_filtering():
    exp = AnalyticsExporter()
    exp.add_records("ext-4", SAMPLE)
    output = exp.export("ext-4", ExportFormat.JSON, date_from="2026-10-25")
    data = json.loads(output)
    assert len(data) == 2


def test_empty_export():
    exp = AnalyticsExporter()
    output = exp.export("nonexistent", ExportFormat.SUMMARY)
    assert "No data" in output
