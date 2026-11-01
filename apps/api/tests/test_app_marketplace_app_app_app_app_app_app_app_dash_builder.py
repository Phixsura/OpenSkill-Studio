from app.services.app_marketplace_app_app_app_app_app_app_app_dash_builder import create_dashboard, dashboard_summary

def test_create():
    r = create_dashboard("System Overview", [
        {"title": "CPU", "type": "gauge", "metric": "cpu_pct", "width": 4},
        {"title": "Memory", "type": "gauge", "metric": "mem_pct", "width": 4},
        {"title": "Requests", "type": "chart", "metric": "rps", "width": 12},
    ])
    assert r["panel_count"] == 3
    assert r["layout"]["total_cells"] == 20

def test_summary():
    dashes = [create_dashboard("A", [{"title": "x"}] * 5),
              create_dashboard("B", [{"title": "y"}] * 3)]
    r = dashboard_summary(dashes)
    assert r["total_dashboards"] == 2
    assert r["total_panels"] == 8
    assert r["avg_panels"] == 4.0
