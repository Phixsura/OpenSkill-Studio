from app.services.app_marketplace_app_app_app_analytics_export import export_analytics

def test_json():
    data = [{"date": "2026-01-01", "installs": 10}, {"date": "2026-01-02", "installs": 20}]
    r = export_analytics(data_points=data, format="json", metrics=["date", "installs"])
    assert r["format"] == "json"
    assert r["row_count"] == 2
    assert '"installs"' in r["content"]

def test_csv():
    data = [{"date": "2026-01-01", "installs": 10}]
    r = export_analytics(data_points=data, format="csv", metrics=["date", "installs"])
    assert r["format"] == "csv"
    assert "date,installs" in r["content"]

def test_empty():
    r = export_analytics(data_points=[], format="json")
    assert r["row_count"] == 0
