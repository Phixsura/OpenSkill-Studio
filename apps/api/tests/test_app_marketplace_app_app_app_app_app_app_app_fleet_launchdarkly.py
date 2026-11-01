from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_launchdarkly import fleet_launchdarkly_status
def test_ld():
    r = fleet_launchdarkly_status([{"active": True, "targeting_on": True, "age_days": 10}, {"active": True, "age_days": 100}])
    assert r["targeting"] == 1
    assert r["stale"] == 1
    assert not r["needs_cleanup"]
