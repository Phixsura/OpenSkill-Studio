from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_namespace_mgr_v9 import fleet_namespace_mgr_v9
def test_ns_v9():
    r = fleet_namespace_mgr_v9([{"active": True, "quota_set": True, "pod_count": 50}])
    assert r["total_pods"] == 50
    assert r["healthy"]
