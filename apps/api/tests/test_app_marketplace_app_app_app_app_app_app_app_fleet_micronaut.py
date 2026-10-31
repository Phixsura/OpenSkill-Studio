from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_micronaut import fleet_micronaut_status
def test_mn():
    r = fleet_micronaut_status([{"running": True, "graalvm": True, "memory_mb": 128}])
    assert r["graalvm"] == 1
    assert r["lightweight"]
