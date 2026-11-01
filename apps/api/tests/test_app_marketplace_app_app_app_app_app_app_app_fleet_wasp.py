from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wasp import fleet_wasp_status
def test_wasp():
    r = fleet_wasp_status([{"deployed": True, "entities": 20, "operations": 50}])
    assert r["entities"] == 20
    assert r["all_deployed"]
