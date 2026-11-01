from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_qual_v2 import fleet_ai_platform_quality_v2
def test_pqv2():
    r = fleet_ai_platform_quality_v2([{"active": True, "coverage_pct": 92, "bugs_open": 10, "debt_hours": 100}])
    assert r["coverage"] == 92.0
    assert r["quality"]
