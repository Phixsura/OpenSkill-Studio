from app.services.app_marketplace_app_metrics_endpoint import get_metrics
def test_metrics():
    r = get_metrics()
    assert r["http_requests_total"] > 0
    assert r["active_connections"] > 0
