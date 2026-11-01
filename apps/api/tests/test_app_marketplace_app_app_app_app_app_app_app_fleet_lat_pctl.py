from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lat_pctl import fleet_latency_percentiles
def test_percentiles():
    samples = list(range(1, 101))  # 1..100
    r = fleet_latency_percentiles(samples)
    assert r["p50"] == 51
    assert r["p95"] == 96
    assert r["p99"] == 100
