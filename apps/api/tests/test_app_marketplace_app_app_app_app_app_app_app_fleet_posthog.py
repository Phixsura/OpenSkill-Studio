from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_posthog import fleet_posthog_status
def test_ph():
    r = fleet_posthog_status([{"running": True, "events_24h": 2000000, "feature_flags": 50}])
    assert r["events_24h"] == 2000000
    assert r["all_running"]
