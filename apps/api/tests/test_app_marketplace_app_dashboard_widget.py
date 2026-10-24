from app.services.app_marketplace_app_dashboard_widget import create_widget, build_dashboard_layout

def test_create():
    r = create_widget(widget_type="metric_card", title="Total Users")
    assert r["widget_id"].startswith("wgt_")
    assert r["type"] == "metric_card"
    assert r["title"] == "Total Users"

def test_invalid_type():
    r = create_widget(widget_type="rainbow", title="X")
    assert "error" in r

def test_layout():
    widgets = [{"type": "metric_card"}, {"type": "chart"}, {"type": "chart"}]
    r = build_dashboard_layout(widgets=widgets, columns=3)
    assert r["total_widgets"] == 3
    assert "metric_card" in r["types_used"]
