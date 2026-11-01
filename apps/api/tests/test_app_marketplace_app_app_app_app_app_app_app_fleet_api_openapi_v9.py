from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_openapi_v9 import fleet_api_openapi_v9
def test_aoapi_v9():
    r = fleet_api_openapi_v9([{"generated": True, "lint_passed": True, "lint_errors": 0}])
    assert r["linted"] == 1
    assert r["healthy"]
