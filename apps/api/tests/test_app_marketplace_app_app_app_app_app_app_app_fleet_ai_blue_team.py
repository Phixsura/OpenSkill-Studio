from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_blue_team import fleet_ai_blue_teaming
def test_bt():
    r = fleet_ai_blue_teaming([{"active": True, "incidents": 100, "detections_24h": 500, "response_min": 5}])
    assert r["incidents"] == 100
    assert r["defensive"]
