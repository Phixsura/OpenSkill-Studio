from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_team_mgr import fleet_ai_team_manager
def test_tm():
    r = fleet_ai_team_manager([{"active": True, "teams": 50, "members": 500, "projects": 200}])
    assert r["teams"] == 50
    assert r["organized"]
