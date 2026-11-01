from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gw_mesh import fleet_gateway_mesh
def test_gw_mesh():
    r = fleet_gateway_mesh([{"rps": 5000, "p50_ms": 10, "healthy": True}, {"rps": 3000, "p50_ms": 15, "healthy": True}])
    assert r["total_rps"] == 8000
    assert r["all_healthy"]
