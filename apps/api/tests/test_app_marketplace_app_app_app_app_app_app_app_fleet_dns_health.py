from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns_health import fleet_dns_health
def test_dns_health():
    r = fleet_dns_health([{"resolved": True, "latency_ms": 10}, {"resolved": True, "latency_ms": 200}, {"resolved": False, "latency_ms": 0}])
    assert r["healthy"] == 2
    assert r["failed"] == 1
    assert r["slow"] == 1
    assert not r["all_ok"]
