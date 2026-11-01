from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_moderation import fleet_ai_moderation
def test_mod():
    r = fleet_ai_moderation([{"active": True, "items_24h": 10000000, "flagged_24h": 50000}])
    assert r["flag_rate_pct"] == 0.5
