from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sentry import fleet_sentry_status
def test_sentry():
    r = fleet_sentry_status([{"events_24h": 5000, "unresolved_issues": 10, "crash_free_pct": 99.5}])
    assert r["events_24h"] == 5000
    assert r["healthy"]
