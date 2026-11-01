from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_documentation_v9 import fleet_api_documentation_v9
def test_adoc_v9():
    r = fleet_api_documentation_v9([{"documented": True, "has_examples": True, "openapi_spec": True}])
    assert r["documented"] == 1
    assert r["healthy"]
