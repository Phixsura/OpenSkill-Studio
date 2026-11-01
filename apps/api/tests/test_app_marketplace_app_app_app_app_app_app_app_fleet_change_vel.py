from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_change_vel import fleet_change_velocity
def test_velocity():
    r = fleet_change_velocity({"deploys": 50, "hours": 24})
    assert r["rate_per_hour"] == 2.08
    assert r["high_velocity"]
