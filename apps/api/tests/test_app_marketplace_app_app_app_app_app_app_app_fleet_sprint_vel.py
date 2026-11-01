from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sprint_vel import fleet_sprint_velocity
def test_vel():
    r = fleet_sprint_velocity([{"completed_points": 30}, {"completed_points": 35}, {"completed_points": 40}])
    assert r["avg_velocity"] == 35.0
    assert r["trend"] == "improving"
