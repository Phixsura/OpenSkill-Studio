from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_adopt_curve import fleet_adoption_curve
def test_curve():
    r = fleet_adoption_curve([{"active_users": 100}, {"active_users": 150}, {"active_users": 200}])
    assert r["current_users"] == 200
    assert r["growth_pct"] == 100.0
    assert r["accelerating"]
