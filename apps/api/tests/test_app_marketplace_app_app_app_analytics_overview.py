from app.services.app_marketplace_app_app_app_analytics_overview import build_analytics_overview

def test_overview():
    r = build_analytics_overview(app_id="a1", installs=1000, uninstalls=100,
                                  active_users=600, api_calls=50000,
                                  avg_rating=4.5, reviews=120)
    assert r["net_installs"] == 900
    assert r["health"] == "good"
    assert len(r["metrics"]) == 6
    retention = next(m for m in r["metrics"] if m["label"] == "Retention")
    assert retention["display"] == "60.0%"

def test_poor_health():
    r = build_analytics_overview(app_id="a2", installs=100, uninstalls=80,
                                  active_users=10, api_calls=50,
                                  avg_rating=2.5, reviews=5)
    assert r["health"] == "needs_attention"
