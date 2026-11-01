from app.services.app_marketplace_app_app_app_app_app_app_app_metric_explorer import search_metrics, metric_catalog_summary

def test_search():
    r = search_metrics("http")
    assert r["total"] == 2
    r2 = search_metrics("http", metric_type="counter")
    assert r2["total"] == 1

def test_summary():
    r = metric_catalog_summary()
    assert r["total_metrics"] == 8
    assert "gauge" in r["by_type"]
    assert "counter" in r["by_type"]
