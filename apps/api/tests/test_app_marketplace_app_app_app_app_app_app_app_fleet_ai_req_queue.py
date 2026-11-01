from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_req_queue import fleet_ai_request_queue
def test_rq():
    r = fleet_ai_request_queue([{"active": True, "depth": 500, "throughput_rps": 50000, "avg_wait_ms": 25}])
    assert r["throughput_rps"] == 50000
    assert r["fast"]
