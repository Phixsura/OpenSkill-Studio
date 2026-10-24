from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wid import fleet_workload_identity
def test_wid():
    r = fleet_workload_identity([{"workload_identity": True}, {"workload_identity": False, "uses_sa_keys": True}])
    assert r["workload_identity"] == 1
    assert r["sa_keys"] == 1
    assert not r["modern"]
