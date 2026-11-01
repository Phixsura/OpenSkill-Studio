from app.services.app_marketplace_app_app_app_app_app_app_app_metrics_exporter import export_prometheus, build_platform_metrics

def test_export():
    metrics = build_platform_metrics(requests_total=1000000, errors_total=500,
                                      latency_avg_ms=85.5, active_users=3200, apps_count=450)
    r = export_prometheus(metrics)
    assert r["metric_count"] == 5
    assert "platform_requests_total" in r["text"]
    assert "1000000" in r["text"]
    assert "# TYPE platform_latency_avg_ms gauge" in r["text"]

def test_labels():
    metrics = [{"name": "http_requests", "type": "counter", "value": 100,
                "labels": {"method": "GET", "status": "200"}}]
    r = export_prometheus(metrics)
    assert 'method="GET"' in r["text"]
    assert 'status="200"' in r["text"]
