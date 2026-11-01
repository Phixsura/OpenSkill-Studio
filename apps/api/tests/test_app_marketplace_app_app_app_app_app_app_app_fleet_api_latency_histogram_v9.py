from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_latency_histogram_v9 import fleet_api_latency_histogram_v9
def test_alh_v9():
    r = fleet_api_latency_histogram_v9([{"under_10ms_pct": 60, "under_50ms_pct": 90, "under_100ms_pct": 99}])
    assert r["under_100ms_pct"] == 99.0
    assert r["healthy"]
