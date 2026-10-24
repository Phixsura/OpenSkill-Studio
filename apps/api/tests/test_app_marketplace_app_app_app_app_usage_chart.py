from app.services.app_marketplace_app_app_app_app_usage_chart import build_usage_chart

def test_chart():
    points = [
        {"date": "2026-10-01", "api_calls": 1000},
        {"date": "2026-10-02", "api_calls": 1500},
        {"date": "2026-10-03", "api_calls": 1200},
    ]
    r = build_usage_chart(data_points=points, metric="api_calls")
    assert r["total"] == 3700
    assert r["peak"] == 1500
    assert r["trend"] == "up"
    assert r["data_points"] == 3

def test_empty():
    r = build_usage_chart(data_points=[])
    assert r["total"] == 0
    assert r["trend"] == "flat"
