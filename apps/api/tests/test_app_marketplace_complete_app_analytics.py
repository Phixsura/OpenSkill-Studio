from app.services.app_marketplace_complete_app_analytics import build_complete_app_analytics

def test_with_revenue():
    p = build_complete_app_analytics(
        app={"id": "a1", "name": "App"}, installs={"total": 500}, api_usage={"calls": 10000},
        reviews={"avg": 4.5}, retention={"rate": 85}, revenue={"mrr": 9900},
        geo={"countries": 10}, funnel={"conversion": 5})
    assert p["page_type"] == "complete_app_analytics"
    assert len(p["panels"]) == 7
    assert len(p["time_ranges"]) == 5

def test_without_revenue():
    p = build_complete_app_analytics(
        app={"id": "a1", "name": "App"}, installs={}, api_usage={},
        reviews={}, retention={}, revenue=None, geo={}, funnel={})
    assert len(p["panels"]) == 6
