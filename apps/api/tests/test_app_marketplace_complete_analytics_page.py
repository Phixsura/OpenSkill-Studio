from app.services.app_marketplace_complete_analytics_page import build_complete_analytics_page

def test_with_revenue():
    p = build_complete_analytics_page(
        app={"id": "a1", "name": "App"},
        installs_data={"total": 100}, api_usage={"calls": 5000},
        error_data={"rate": 0.5}, revenue_data={"mrr": 999})
    assert p["page_type"] == "analytics_dashboard"
    assert len(p["panels"]) == 4

def test_without_revenue():
    p = build_complete_analytics_page(
        app={"id": "a1", "name": "App"},
        installs_data={}, api_usage={}, error_data={})
    assert len(p["panels"]) == 3
