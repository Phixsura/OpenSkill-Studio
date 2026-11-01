from app.services.app_marketplace_extension_mktplace_dashboard import MktplaceDashboardService

def test_add_widget():
    svc = MktplaceDashboardService()
    svc.add_widget("u1", "Installs", "counter", {"value": 500})
    dash = svc.get_dashboard("u1")
    assert len(dash) == 1
    assert dash[0].data["value"] == 500

def test_remove():
    svc = MktplaceDashboardService()
    w = svc.add_widget("u1", "Widget", "chart", {})
    svc.remove_widget("u1", w.widget_id)
    assert len(svc.get_dashboard("u1")) == 0

def test_reorder():
    svc = MktplaceDashboardService()
    w1 = svc.add_widget("u1", "A", "counter", {})
    w2 = svc.add_widget("u1", "B", "counter", {})
    svc.reorder("u1", [w2.widget_id, w1.widget_id])
    dash = svc.get_dashboard("u1")
    assert dash[0].widget_id == w2.widget_id

def test_defaults():
    svc = MktplaceDashboardService()
    defaults = svc.get_default_dashboard()
    assert len(defaults) == 4
