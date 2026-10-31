from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spiffe import fleet_spiffe_status
def test_spiffe():
    r = fleet_spiffe_status([{"has_svid": True}, {"has_svid": True, "svid_expired": True}, {"has_svid": False}])
    assert r["with_svid"] == 2
    assert r["expired"] == 1
    assert not r["healthy"]
