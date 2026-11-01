from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_scale import fleet_ai_platform_scalability
def test_ps():
    r = fleet_ai_platform_scalability([{"active": True, "max_rps": 10000000, "current_rps": 5000000, "auto": True}])
    assert r["headroom_pct"] == 50.0
    assert r["scalable"]
