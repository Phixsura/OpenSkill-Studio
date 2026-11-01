from app.services.app_marketplace_app_app_app_comparison import compare_apps_metrics

def test_compare():
    apps = [
        {"id": "a", "name": "AppA", "rating": 4.5, "downloads": 10000, "review_count": 50,
         "response_time_ms": 120, "uptime_pct": 99.9},
        {"id": "b", "name": "AppB", "rating": 4.8, "downloads": 5000, "review_count": 80,
         "response_time_ms": 80, "uptime_pct": 99.99},
    ]
    r = compare_apps_metrics(apps=apps)
    assert r["app_count"] == 2
    assert r["metric_count"] == 5
    rating = next(c for c in r["comparison"] if c["metric"] == "rating")
    assert rating["best"] == "b"
    downloads = next(c for c in r["comparison"] if c["metric"] == "downloads")
    assert downloads["best"] == "a"
