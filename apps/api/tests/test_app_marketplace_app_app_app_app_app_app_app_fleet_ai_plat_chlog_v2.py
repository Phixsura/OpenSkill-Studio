from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_chlog_v2 import fleet_ai_platform_changelog_v2
def test_pcv2():
    r = fleet_ai_platform_changelog_v2([{"active": True, "releases": 200, "features": 1000, "fixes": 500, "subscribers": 50000}])
    assert r["releases"] == 200
    assert r["publishing"]
