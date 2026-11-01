from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_canary import fleet_canary_status
def test_canary():
    r = fleet_canary_status([{"phase": "canary"}, {"phase": "promoted"}, {"phase": "failed"}])
    assert r["active_canaries"] == 1
    assert r["promoted"] == 1
    assert r["failed"] == 1
