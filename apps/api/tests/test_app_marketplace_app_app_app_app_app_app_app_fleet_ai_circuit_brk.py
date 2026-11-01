from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_circuit_brk import fleet_ai_circuit_breaker
def test_cb():
    r = fleet_ai_circuit_breaker([{"state": "closed", "trips_24h": 2}, {"state": "closed", "trips_24h": 0}])
    assert r["closed"] == 2
    assert r["stable"]
