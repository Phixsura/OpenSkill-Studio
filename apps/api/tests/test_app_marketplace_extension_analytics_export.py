from app.services.app_marketplace_extension_analytics_export import ExtAnalyticsExportService

def test_record_and_report():
    svc = ExtAnalyticsExportService()
    svc.record_event("ext-1", "install")
    svc.record_event("ext-1", "install")
    svc.record_event("ext-1", "view", 5)
    report = svc.generate_report("ext-1")
    assert report.metrics["total_events"] == 3
    assert report.metrics["by_event"]["install"] == 2

def test_export_json():
    svc = ExtAnalyticsExportService()
    svc.record_event("ext-1", "click")
    report = svc.generate_report("ext-1")
    data = svc.export_json(report.report_id)
    assert '"click"' in data
    assert '"period": "daily"' in data

def test_list_reports():
    svc = ExtAnalyticsExportService()
    svc.generate_report("ext-1")
    svc.generate_report("ext-1", "weekly")
    svc.generate_report("ext-2")
    assert len(svc.list_reports("ext-1")) == 2
