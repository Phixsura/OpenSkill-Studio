from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_qual import fleet_ai_data_quality
def test_dq():
    r = fleet_ai_data_quality([{"active": True, "datasets": 500, "checks_24h": 50000, "quality": 96}])
    assert r["quality"] == 96.0
    assert r["high_quality"]
