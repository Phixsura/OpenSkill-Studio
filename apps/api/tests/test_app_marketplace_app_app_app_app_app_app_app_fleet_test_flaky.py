from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_test_flaky import fleet_test_flakiness
def test_flaky():
    r = fleet_test_flakiness([{"flaky": False}, {"flaky": True}, {"flaky": False}] * 10 + [{"flaky": False}] * 70)
    assert r["flaky"] == 10
    assert r["total"] == 100
    assert r["flaky_rate_pct"] == 10.0
    assert not r["acceptable"]
