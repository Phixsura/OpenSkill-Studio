from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_security_event_v9 import fleet_security_event_v9
def test_se2_v9():
    r = fleet_security_event_v9([{"severity": "low", "investigated": True}])
    assert r["critical"] == 0
    assert r["healthy"]
