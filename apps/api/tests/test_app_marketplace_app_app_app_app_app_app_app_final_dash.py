from app.services.app_marketplace_app_app_app_app_app_app_app_final_dash import build_final_dashboard

def test_dashboard():
    r = build_final_dashboard(total_apps=500, total_devs=200, total_installs=2500000,
                                total_api_calls=50000000, uptime_pct=99.95, avg_rating=4.5,
                                active_users=8000, revenue_mrr=125000,
                                open_incidents=0, pending_reviews=3)
    assert r["health_score"] == 100
    assert r["status"] == "excellent"
    assert r["metrics"]["apps"]["display"] == "500"
    assert r["metrics"]["mrr"]["display"] == "$125,000"
    assert not r["alerts"]["has_alerts"]
