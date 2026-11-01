from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resp_size import fleet_response_size
def test_size():
    r = fleet_response_size([{"avg_response_kb": 50}, {"avg_response_kb": 2000}])
    assert r["avg_response_kb"] == 1025.0
    assert r["large_responses"] == 1
    assert not r["optimized"]
