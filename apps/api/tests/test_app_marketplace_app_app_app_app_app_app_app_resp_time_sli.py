from app.services.app_marketplace_app_app_app_app_app_app_app_resp_time_sli import calculate_sli, sli_trend

def test_sli():
    latencies = [50, 100, 150, 200, 250, 300]
    r = calculate_sli(latencies, threshold_ms=200)
    assert r["good_count"] == 4  # 50, 100, 150, 200
    assert r["sli_pct"] == 66.667
    assert r["samples"] == 6

def test_trend():
    r = sli_trend([{"sli_pct": 99.5}, {"sli_pct": 99.9}])
    assert r["trend"] == "improving"
    assert r["delta"] == 0.4
