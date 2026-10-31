from app.services.app_marketplace_app_app_app_app_app_app_app_metric_agg import aggregate_metrics, downsample

def test_aggregate():
    r = aggregate_metrics([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    assert r["count"] == 10
    assert r["avg"] == 55.0
    assert r["min"] == 10
    assert r["max"] == 100
    assert r["p50"] == 60

def test_downsample():
    points = [{"timestamp": i, "value": i * 10} for i in range(20)]
    r = downsample(points, factor=5)
    assert len(r) == 4
    assert r[0]["count"] == 5
    assert r[0]["avg"] == 20.0  # avg of 0,10,20,30,40
