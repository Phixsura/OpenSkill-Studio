from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_boundary import fleet_boundary_status
def test_boundary():
    r = fleet_boundary_status([{"active_sessions": 5, "authorized": True}, {"active_sessions": 3, "authorized": True}])
    assert r["active_sessions"] == 8
    assert r["all_authorized"]
