from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_adopt import fleet_ai_platform_adoption
def test_pa():
    r = fleet_ai_platform_adoption([{"active": True, "signups_24h": 1000, "activated": 500, "retained": 400}])
    assert r["conversion"] == 50.0
    assert r["growing"]
