from app.services.app_marketplace_app_app_app_app_app_app_app_user_dash_summary import build_user_dashboard

def test_dashboard():
    r = build_user_dashboard(user_name="Alice", org_name="Acme", plan="pro",
                               app_count=5, api_calls_today=150000,
                               unread_notifications=15, recent_deploys=3,
                               health_score=92, open_tickets=2)
    assert "Alice" in r["greeting"]
    assert len(r["quick_stats"]) == 6
    assert r["quick_stats"][1]["value"] == "150,000"
    assert len(r["alerts"]) == 1  # notifications > 10
