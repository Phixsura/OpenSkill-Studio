from app.services.app_marketplace_app_developer_stats_card import build_stats_card

def test_build():
    stats = {"app_count": 5, "total_installs": 10000, "revenue": 2500,
             "avg_rating": 4.6, "review_count": 85, "api_calls": 50000,
             "install_change": 500, "revenue_change": 200}
    r = build_stats_card(stats=stats)
    assert r["total_cards"] == 6
    installs = next(c for c in r["cards"] if c["id"] == "installs")
    assert installs["value"] == 10000
    assert installs["change"] == 500

def test_empty():
    r = build_stats_card(stats={})
    assert r["total_cards"] == 6
    assert all(c["value"] == 0 for c in r["cards"])
