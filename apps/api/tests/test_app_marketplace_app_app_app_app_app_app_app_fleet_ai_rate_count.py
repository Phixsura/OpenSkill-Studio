from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rate_count import fleet_ai_rate_counter
def test_rc():
    r = fleet_ai_rate_counter([{"active": True, "rps": 500000, "peak_rps": 1000000, "windows": 10}])
    assert r["rps"] == 500000
    assert r["tracking"]
