from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_roadmap_v7 import fleet_ai_roadmap_v7
def test_rv7():
    r = fleet_ai_roadmap_v7([{"active": True, "planned": 200, "in_progress": 50, "shipped": 500, "on_time_pct": 92}])
    assert r["shipped"] == 500
    assert r["executing"]
