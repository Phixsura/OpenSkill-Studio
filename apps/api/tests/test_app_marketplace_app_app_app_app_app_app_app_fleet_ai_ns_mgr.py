from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ns_mgr import fleet_ai_namespace_manager
def test_nm():
    r = fleet_ai_namespace_manager([{"active": True, "namespaces": 100, "resources": 5000, "conflicts": 0}])
    assert r["namespaces"] == 100
    assert r["clean"]
