from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_cdn_v2 import fleet_ai_cdn_v2
def test_cv2():
    r = fleet_ai_cdn_v2([{"active": True, "pops": 300, "bandwidth_tb": 5000, "cache_hit_pct": 97}])
    assert r["pops"] == 300
    assert r["performant"]
