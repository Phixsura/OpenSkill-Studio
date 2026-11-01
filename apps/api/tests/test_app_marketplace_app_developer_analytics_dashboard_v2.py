from app.services.app_marketplace_app_developer_analytics_dashboard_v2 import build_analytics_dashboard_v2, compute_sparkline

def test_dashboard():
    d = build_analytics_dashboard_v2(
        app={"id": "a1", "name": "App"},
        metrics={"installs": 500, "api_calls": 10000, "errors": 5, "avg_response_ms": 120},
        trends={"installs": 10, "api_calls": -5},
        top_endpoints=[{"path": "/users", "count": 5000}])
    assert d["page_type"] == "analytics_v2"
    assert len(d["cards"]) == 4

def test_sparkline():
    s = compute_sparkline(data_points=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], width=5)
    assert len(s) == 5

def test_sparkline_short():
    s = compute_sparkline(data_points=[1, 2], width=5)
    assert len(s) == 5
