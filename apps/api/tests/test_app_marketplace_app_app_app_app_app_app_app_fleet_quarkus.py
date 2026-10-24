from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_quarkus import fleet_quarkus_status
def test_qk():
    r = fleet_quarkus_status([{"running": True, "native": True, "startup_ms": 50}])
    assert r["native"] == 1
    assert r["fast"]
