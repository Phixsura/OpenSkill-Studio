from app.services.app_marketplace_app_metric_aggregator import aggregate_metrics

def test_avg():
    points = [{"timestamp": 0, "value": 10}, {"timestamp": 30, "value": 20},
              {"timestamp": 90, "value": 50}]
    r = aggregate_metrics(data_points=points, interval_sec=60, aggregation="avg")
    assert r["bucket_count"] == 2
    assert r["buckets"][0]["value"] == 15.0  # avg of 10,20

def test_sum():
    points = [{"timestamp": 0, "value": 5}, {"timestamp": 10, "value": 3}]
    r = aggregate_metrics(data_points=points, interval_sec=60, aggregation="sum")
    assert r["buckets"][0]["value"] == 8

def test_empty():
    r = aggregate_metrics(data_points=[], interval_sec=60)
    assert r["total_points"] == 0

def test_invalid():
    r = aggregate_metrics(data_points=[{"timestamp": 0, "value": 1}], aggregation="median")
    assert "error" in r
