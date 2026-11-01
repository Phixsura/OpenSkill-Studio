from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_trace_sampling_v9 import fleet_trace_sampling_v9
def test_ts2_v9():
    r = fleet_trace_sampling_v9([{"active": True, "rate_pct": 10, "sampled_today": 100000}])
    assert r["avg_rate_pct"] == 10.0
    assert r["healthy"]
