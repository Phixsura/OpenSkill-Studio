from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_startup_prb import fleet_ai_startup_probe
def test_sp():
    r = fleet_ai_startup_probe([{"active": True, "services": 200, "startup_s": 15, "failures": 0}])
    assert r["startup_s"] == 15.0
    assert r["healthy"]
