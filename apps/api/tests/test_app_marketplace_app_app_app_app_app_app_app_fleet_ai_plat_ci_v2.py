from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_ci_v2 import fleet_ai_platform_ci_v2
def test_pciv2():
    r = fleet_ai_platform_ci_v2([{"active": True, "builds_24h": 2000, "pass_rate": 99, "duration_min": 8}])
    assert r["builds_24h"] == 2000
    assert r["green"]
