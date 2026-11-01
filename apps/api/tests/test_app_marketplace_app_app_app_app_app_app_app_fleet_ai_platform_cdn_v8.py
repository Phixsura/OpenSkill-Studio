from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_cdn_v8 import fleet_ai_cdn_v8
def test_cv8():
    r = fleet_ai_cdn_v8([{"active": True, "pops": 500, "pbps": 10, "hit_pct": 98}])
    assert r["pops"] == 500
    assert r["optimal"]
