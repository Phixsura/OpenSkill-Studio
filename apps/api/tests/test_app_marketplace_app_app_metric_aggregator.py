from app.services.app_marketplace_app_app_metric_aggregator import aggregate_metrics, percentile

def test_aggregate():
    points = [
        {"timestamp": "2026-01-01T10:15:00Z", "value": 100},
        {"timestamp": "2026-01-01T10:45:00Z", "value": 200},
        {"timestamp": "2026-01-01T11:15:00Z", "value": 150},
    ]
    r = aggregate_metrics(data_points=points)
    assert r["total_points"] == 3
    assert r["bucket_count"] == 2
    assert r["global_avg"] == 150.0

def test_percentile():
    vals = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    assert percentile(values=vals, p=50) == 55.0
    assert percentile(values=vals, p=90) == 91.0
    assert percentile(values=vals, p=0) == 10
