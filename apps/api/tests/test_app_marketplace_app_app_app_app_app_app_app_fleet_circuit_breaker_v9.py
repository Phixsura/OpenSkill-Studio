from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_circuit_breaker_v9 import fleet_circuit_breaker_v9
def test_cb_v9():
    r = fleet_circuit_breaker_v9([{"state": "closed"}, {"state": "closed"}])
    assert r["closed"] == 2
    assert r["open"] == 0
    assert r["healthy"]
