from app.services.app_marketplace_app_app_app_app_app_app_app_app_analytics import compute_app_analytics

def test_analytics():
    r = compute_app_analytics(app_id="myapp", installs=1000, uninstalls=50,
                                api_calls=500000, active_users=800,
                                errors=100, avg_response_ms=85,
                                rating=4.5, reviews=120)
    assert r["net_installs"] == 950
    assert r["retention_pct"] == 80.0
    assert r["error_rate"] == 0.02
    assert r["health"] == "excellent"
    assert r["api_display"] == "500,000"
