from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_federation_v9 import fleet_cluster_federation_v9
def test_cf2_v9():
    r = fleet_cluster_federation_v9([{"federated": True, "synced": True, "shared_resources": 200}])
    assert r["federated"] == 1
    assert r["healthy"]
