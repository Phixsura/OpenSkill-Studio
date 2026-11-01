from app.services.app_marketplace_app_app_app_support_page import build_support_page

def test_support():
    r = build_support_page(open_tickets=3, recent_incidents=1)
    assert r["resource_count"] == 6
    assert r["open_tickets"] == 3
    assert r["has_alerts"]

def test_no_alerts():
    r = build_support_page()
    assert not r["has_alerts"]
