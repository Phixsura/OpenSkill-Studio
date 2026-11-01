from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_newrelic import fleet_newrelic_status
def test_nr():
    r = fleet_newrelic_status([{"reporting": True, "apdex": 0.95, "error_rate_pct": 0.5}])
    assert r["apdex_avg"] == 0.95
    assert r["healthy"]
