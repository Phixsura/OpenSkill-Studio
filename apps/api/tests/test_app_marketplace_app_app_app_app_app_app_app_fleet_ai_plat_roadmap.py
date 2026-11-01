from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_roadmap import fleet_ai_platform_roadmap
def test_pr():
    r = fleet_ai_platform_roadmap([{"active": True, "planned": 100, "in_progress": 30, "completed": 200}])
    assert r["completed"] == 200
    assert r["executing"]
