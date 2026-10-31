from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cb_v2 import fleet_ai_circuit_breaker_v2
def test_cbv2():
    r = fleet_ai_circuit_breaker_v2([{"active": True, "state": "closed", "trips_24h": 3}])
    assert r["closed"] == 1
    assert r["stable"]
