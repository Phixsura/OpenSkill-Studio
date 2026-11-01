from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_semkernel import fleet_semantic_kernel
def test_sk():
    r = fleet_semantic_kernel([{"active": True, "plugins": 20, "invocations_24h": 100000}])
    assert r["plugins"] == 20
    assert r["all_active"]
