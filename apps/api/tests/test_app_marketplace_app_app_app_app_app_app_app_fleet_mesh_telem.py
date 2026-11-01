from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_telem import fleet_mesh_telemetry
def test_telem():
    r = fleet_mesh_telemetry([{"rps": 1000, "latency_ms": 5, "error_count": 0}, {"rps": 2000, "latency_ms": 10, "error_count": 3}])
    assert r["total_rps"] == 3000
    assert r["errors"] == 3
    assert not r["healthy"]
