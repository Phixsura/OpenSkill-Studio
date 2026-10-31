from app.services.app_marketplace_extension_stats_exporter import MktplaceStatsExporterService

def test_capture():
    svc = MktplaceStatsExporterService()
    svc.capture({"extensions": 500, "users": 1000})
    latest = svc.get_latest()
    assert latest["data"]["extensions"] == 500

def test_export_json():
    svc = MktplaceStatsExporterService()
    svc.capture({"a": 1})
    data = svc.export_json()
    assert '"a": 1' in data

def test_export_csv():
    svc = MktplaceStatsExporterService()
    svc.capture({"extensions": 500, "users": 1000})
    csv = svc.export_csv(["extensions", "users"])
    assert "timestamp,extensions,users" in csv
    assert "500" in csv

def test_trend():
    svc = MktplaceStatsExporterService()
    svc.capture({"dau": 100})
    svc.capture({"dau": 150})
    trend = svc.get_trend("dau")
    assert len(trend) == 2
    assert trend[1][1] == 150
