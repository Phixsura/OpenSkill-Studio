from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_workload_identity_v9 import fleet_workload_identity_v9
def test_wi_v9():
    r = fleet_workload_identity_v9([{"identity_federated": True, "service_account_bound": True, "audience": "api"}])
    assert r["federated"] == 1
    assert r["healthy"]
