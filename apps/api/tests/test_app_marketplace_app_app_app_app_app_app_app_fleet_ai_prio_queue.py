from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prio_queue import fleet_ai_priority_queue
def test_pq():
    r = fleet_ai_priority_queue([{"active": True, "levels": 5, "promoted": 10000, "total_24h": 1000000}])
    assert r["levels"] == 5
    assert r["prioritized"]
