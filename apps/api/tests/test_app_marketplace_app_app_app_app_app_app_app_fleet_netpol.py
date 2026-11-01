from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_netpol import fleet_netpol
def test_netpol():
    r = fleet_netpol([{"has_netpol": True}, {"has_netpol": False}, {"has_netpol": True}])
    assert r["covered"] == 2
    assert r["uncovered"] == 1
    assert not r["full_coverage"]
