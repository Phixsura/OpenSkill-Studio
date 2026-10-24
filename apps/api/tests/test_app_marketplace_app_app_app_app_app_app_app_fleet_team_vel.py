from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_team_vel import fleet_team_velocity
def test_vel():
    r = fleet_team_velocity([{"name": "alpha", "story_points": 50}, {"name": "beta", "story_points": 30}])
    assert r["total_points"] == 80
    assert r["avg_velocity"] == 40.0
    assert r["top_team"] == "alpha"
