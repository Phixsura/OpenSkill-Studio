from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cap_reserve import fleet_capacity_reservation
def test_reserve():
    r = fleet_capacity_reservation([{"reserved_units": 100, "used_units": 30}, {"reserved_units": 100, "used_units": 20}])
    assert r["reserved"] == 200
    assert r["util_pct"] == 25.0
    assert r["waste"]
