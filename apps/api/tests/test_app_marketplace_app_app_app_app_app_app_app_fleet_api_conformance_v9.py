from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_conformance_v9 import fleet_api_conformance_v9
def test_aconf_v9():
    r = fleet_api_conformance_v9([{"passed": True, "standard": "OpenAPI", "violations": 0}])
    assert r["passed"] == 1
    assert r["healthy"]
