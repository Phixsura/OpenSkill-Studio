from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_workers_ai import fleet_workers_ai
def test_wai():
    r = fleet_workers_ai([{"active": True, "inferences_24h": 500000, "avg_latency_ms": 100}])
    assert r["inferences_24h"] == 500000
    assert r["fast"]
