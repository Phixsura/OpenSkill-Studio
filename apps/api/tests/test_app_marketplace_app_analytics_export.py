from app.services.app_marketplace_app_analytics_export import export_analytics

def test_json():
    data = [{"date": "2026-10-01", "installs": 50}, {"date": "2026-10-02", "installs": 60}]
    r = export_analytics(app_id="a1", data=data, fmt="json")
    assert r["mime_type"] == "application/json"
    assert r["row_count"] == 2
    assert '"installs": 50' in r["content"]

def test_csv():
    data = [{"date": "2026-10-01", "installs": 50}]
    r = export_analytics(app_id="a1", data=data, fmt="csv")
    assert "date,installs" in r["content"]
    assert r["mime_type"] == "text/csv"

def test_markdown():
    data = [{"metric": "installs", "value": 100}]
    r = export_analytics(app_id="a1", data=data, fmt="markdown")
    assert "| metric | value |" in r["content"]

def test_empty():
    r = export_analytics(app_id="a1", data=[], fmt="json")
    assert "error" in r
