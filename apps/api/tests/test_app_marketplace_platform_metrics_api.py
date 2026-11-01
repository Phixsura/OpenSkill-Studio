from app.services.app_marketplace_platform_metrics_api import get_platform_metrics

def test_metrics():
    r = get_platform_metrics()
    assert r["status"] == "operational"
    assert len(r["endpoints"]) == 4
