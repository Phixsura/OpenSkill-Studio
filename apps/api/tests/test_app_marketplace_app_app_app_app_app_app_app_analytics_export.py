from app.services.app_marketplace_app_app_app_app_app_app_app_analytics_export import export_analytics

def test_json():
    r = export_analytics(app_id="myapp", metrics=[{"date": "2026-10-24", "calls": 5000}], fmt="json")
    assert r["format"] == "json"
    assert r["record_count"] == 1
    assert "myapp" in r["content"]

def test_csv():
    r = export_analytics(app_id="myapp", metrics=[{"date": "2026-10-24", "calls": 5000}], fmt="csv")
    assert r["format"] == "csv"
    assert "date" in r["content"]
    assert "5000" in r["content"]
