from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cb_status import fleet_cb_status
def test_cb():
    r = fleet_cb_status([{"state": "closed"}, {"state": "open"}, {"state": "half-open"}])
    assert r["open"] == 1
    assert r["half_open"] == 1
    assert r["closed"] == 1
    assert not r["healthy"]
