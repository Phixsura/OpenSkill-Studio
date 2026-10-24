from app.services.app_marketplace_analytics_summary import build_analytics_summary

def test_summary():
    s = build_analytics_summary(total_page_views=10000, unique_visitors=5000, search_count=2000, install_count=500, conversion_rate=5.0)
    assert s["conversion_rate"] == 5.0
    assert s["avg_views_per_install"] == 20.0

def test_zero_installs():
    s = build_analytics_summary(total_page_views=100, unique_visitors=50, search_count=10, install_count=0, conversion_rate=0)
    assert s["avg_views_per_install"] == 0
