from app.services.app_marketplace_complete_developer_analytics_page import build_complete_developer_analytics

def test_with_revenue():
    p = build_complete_developer_analytics(
        apps=[{"name": "A"}, {"name": "B"}], total_installs=5000,
        total_api_calls=100000, avg_rating=4.5, revenue={"mrr": "$99"},
        top_apps=[{"name": "A", "installs": 3000}], install_trend={"data": [10, 20, 30]},
        error_rate=0.5)
    assert len(p["overview"]) == 6  # includes MRR
    assert len(p["charts"]) == 2

def test_without_revenue():
    p = build_complete_developer_analytics(
        apps=[], total_installs=0, total_api_calls=0, avg_rating=0,
        revenue=None, top_apps=[], install_trend={}, error_rate=0)
    assert len(p["overview"]) == 5
