from app.services.app_marketplace_app_app_app_app_app_app_app_dash_widgets import get_widget, build_dashboard_layout, list_widgets

def test_widget():
    w = get_widget("api_calls")
    assert w["title"] == "API Calls"
    assert w["type"] == "metric"

def test_layout():
    r = build_dashboard_layout(["api_calls", "error_rate", "active_users", "revenue", "deploy_status"])
    assert r["count"] == 5
    assert len(r["layout"]) >= 2

def test_list():
    assert len(list_widgets()) == 8
