from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eventbridge import fleet_eventbridge_status
def test_eb():
    r = fleet_eventbridge_status([{"events_24h": 2000000, "rules": 50, "failed_invocations": 0}])
    assert r["events_24h"] == 2000000
    assert r["healthy"]
