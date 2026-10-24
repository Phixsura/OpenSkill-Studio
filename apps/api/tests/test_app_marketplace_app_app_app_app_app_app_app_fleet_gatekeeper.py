from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gatekeeper import fleet_gatekeeper_status
def test_gk():
    r = fleet_gatekeeper_status([{"enforcement": "deny", "violations": 0}, {"enforcement": "dryrun", "violations": 3}])
    assert r["enforced"] == 1
    assert r["violations"] == 3
    assert not r["clean"]
