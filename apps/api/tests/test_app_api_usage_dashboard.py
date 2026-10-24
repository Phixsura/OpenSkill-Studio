from app.services.app_api_usage_dashboard import build_dashboard_data

def test_basic():
    d = build_dashboard_data(apps=[{"id": "a1", "name": "X", "status": "published"}],
                             total_api_calls=500, total_executions=100)
    assert d["summary"]["total_apps"] == 1
    assert d["summary"]["published"] == 1
    assert d["summary"]["api_calls"] == 500

def test_health():
    d = build_dashboard_data(apps=[], health_scores=[90, 100, 80])
    assert d["summary"]["avg_health"] == 90.0

def test_empty():
    d = build_dashboard_data(apps=[])
    assert d["summary"]["total_apps"] == 0
    assert d["summary"]["avg_health"] == 100.0
