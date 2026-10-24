from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spacelift import fleet_spacelift_status
def test_sl():
    r = fleet_spacelift_status([{"tracked": True, "policies": 5}, {"tracked": True, "drifted": True, "policies": 3}])
    assert r["drifted"] == 1
    assert r["policies"] == 8
    assert not r["clean"]
