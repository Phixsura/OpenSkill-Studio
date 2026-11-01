from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cdn import fleet_ai_cdn
def test_cdn():
    r = fleet_ai_cdn([{"active": True, "pops": 200, "bandwidth_tb": 500, "cache_hit_pct": 95}])
    assert r["pops"] == 200
    assert r["efficient"]
