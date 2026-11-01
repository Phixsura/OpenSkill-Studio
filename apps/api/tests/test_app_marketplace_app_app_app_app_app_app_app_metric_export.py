from app.services.app_marketplace_app_app_app_app_app_app_app_metric_export import export_prometheus, metrics_summary

def test_export():
    output = export_prometheus([
        {"name": "http_requests_total", "type": "counter", "value": 1000,
         "labels": {"method": "GET", "status": "200"}, "help": "Total HTTP requests"},
        {"name": "cpu_usage", "type": "gauge", "value": 0.75, "help": "CPU usage"},
    ])
    assert 'http_requests_total{method="GET",status="200"} 1000' in output
    assert "cpu_usage 0.75" in output

def test_summary():
    r = metrics_summary([
        {"name": "a", "type": "counter", "value": 1, "labels": {"x": "y"}},
        {"name": "b", "type": "gauge", "value": 2},
    ])
    assert r["total"] == 2
    assert r["with_labels"] == 1
