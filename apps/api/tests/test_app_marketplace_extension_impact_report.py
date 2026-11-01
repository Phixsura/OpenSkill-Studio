from app.services.app_marketplace_extension_impact_report import ExtensionImpactReportService


def test_record_and_report():
    svc = ExtensionImpactReportService()
    svc.record("ext-1", hours_saved_monthly=40, errors_prevented=150,
               tasks_automated=500, cost_savings_cents=200000)
    report = svc.get_report("ext-1")
    assert report["hours_saved"] == 40
    assert report["annual_hours_saved"] == 480
    assert report["annual_savings"] == 2400000


def test_compare():
    svc = ExtensionImpactReportService()
    svc.record("ext-1", hours_saved_monthly=40)
    svc.record("ext-2", hours_saved_monthly=20)
    comparison = svc.compare(["ext-1", "ext-2"])
    assert len(comparison) == 2
    assert comparison[0]["hours_saved"] == 40


def test_top_impact():
    svc = ExtensionImpactReportService()
    svc.record("a", hours_saved_monthly=10)
    svc.record("b", hours_saved_monthly=50)
    svc.record("c", hours_saved_monthly=30)
    top = svc.get_top_impact("hours_saved_monthly", 2)
    assert top[0].extension_id == "b"
    assert len(top) == 2


def test_empty_report():
    svc = ExtensionImpactReportService()
    report = svc.get_report("nonexistent")
    assert report["hours_saved"] == 0
