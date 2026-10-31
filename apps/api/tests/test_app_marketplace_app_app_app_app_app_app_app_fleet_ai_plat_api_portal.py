from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_api_portal import fleet_ai_api_portal_v2
def test_apv2():
    r = fleet_ai_api_portal_v2([{"active": True, "apis": 500, "pages": 5000, "developers": 100000, "api_keys": 200000}])
    assert r["apis"] == 500
    assert r["adopted"]
