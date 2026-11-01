from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_coverage import calculate_coverage

def test_coverage():
    r = calculate_coverage([
        {"path": "/users", "method": "GET", "has_test": True},
        {"path": "/users", "method": "POST", "has_test": True},
        {"path": "/orders", "method": "GET", "has_test": False},
        {"path": "/health", "method": "GET", "has_test": True},
    ])
    assert r["coverage_pct"] == 75
    assert r["uncovered_count"] == 1
    assert "/orders" in r["uncovered_paths"]
    assert r["by_method"]["GET"]["covered"] == 2
