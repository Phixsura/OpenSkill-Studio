from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_secret_rot import fleet_ai_secret_rotation
def test_sr():
    r = fleet_ai_secret_rotation([{"active": True, "secrets": 500, "rotations_24h": 50, "avg_age_days": 15}])
    assert r["secrets"] == 500
    assert r["fresh"]
