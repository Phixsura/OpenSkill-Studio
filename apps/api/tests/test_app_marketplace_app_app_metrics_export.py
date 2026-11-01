from app.services.app_marketplace_app_app_metrics_export import export_prometheus, build_dashboard_metrics

def test_export():
    metrics = [
        {"name": "http.requests", "value": 1000, "type": "counter", "help": "Total requests",
         "labels": {"method": "GET"}},
        {"name": "cpu.usage", "value": 42.5, "type": "gauge", "help": "CPU %"},
    ]
    r = export_prometheus(metrics=metrics)
    assert r["metric_count"] == 2
    assert "# TYPE http_requests counter" in r["content"]
    assert 'method="GET"' in r["content"]
    assert "cpu_usage 42.5" in r["content"]

def test_dashboard():
    r = build_dashboard_metrics(app_id="a1")
    assert len(r["metrics"]) == 4
    assert r["metrics"][0]["name"] == "app.requests.total"
