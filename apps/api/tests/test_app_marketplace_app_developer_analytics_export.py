from app.services.app_marketplace_app_developer_analytics_export import build_analytics_export, format_export

def test_build():
    r = build_analytics_export(app_id="a1", period="2026-10", sections=["installs", "errors"])
    assert r["status"] == "generating"

def test_invalid_section():
    r = build_analytics_export(app_id="a1", period="2026-10", sections=["magic"])
    assert r["error"]

def test_format_json():
    r = format_export(data={"total": 100}, fmt="json")
    assert '"total": 100' in r

def test_format_csv():
    r = format_export(data={"rows": [{"date": "2026-01", "count": 10}]}, fmt="csv")
    assert "date,count" in r
    assert "2026-01,10" in r
