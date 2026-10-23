from app.services.app_marketplace_metrics_export import export_metrics_json, export_metrics_csv, build_export_options, estimate_export_size

def test_json():
    r = export_metrics_json(metrics={"installs": 500}, app_name="App", period="Oct 2026")
    parsed = __import__("json").loads(r)
    assert parsed["app"] == "App"
    assert parsed["metrics"]["installs"] == 500

def test_csv():
    data = [{"date": "2026-10-01", "installs": 50}, {"date": "2026-10-02", "installs": 60}]
    r = export_metrics_csv(data_points=data, columns=["date", "installs"])
    assert "date,installs" in r
    assert "2026-10-01,50" in r

def test_options():
    o = build_export_options(available_metrics=["installs"])
    assert len(o) == 3

def test_size():
    s = estimate_export_size(metric_count=5, data_points=100, format="json")
    assert s["estimated_bytes"] > 0
