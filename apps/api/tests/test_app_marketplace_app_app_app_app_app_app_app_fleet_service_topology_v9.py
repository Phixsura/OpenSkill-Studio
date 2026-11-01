from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_topology_v9 import fleet_service_topology_v9
def test_st2_v9():
    r = fleet_service_topology_v9([{"dependencies": ["a", "b"], "dependents": ["c"]}])
    assert r["edges"] == 2
    assert r["healthy"]
