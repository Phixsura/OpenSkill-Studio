from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_engagement import fleet_user_engagement
def test_engage():
    r = fleet_user_engagement({"dau": 500, "mau": 2000, "avg_session_min": 15})
    assert r["stickiness_pct"] == 25.0
    assert r["engaged"]
