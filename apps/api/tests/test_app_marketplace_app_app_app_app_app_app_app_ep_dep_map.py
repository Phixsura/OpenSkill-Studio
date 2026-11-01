from app.services.app_marketplace_app_app_app_app_app_app_app_ep_dep_map import map_endpoint_deps

def test_map():
    r = map_endpoint_deps([
        {"endpoint": "/api/orders", "downstream_service": "user-svc"},
        {"endpoint": "/api/orders", "downstream_service": "payment-svc"},
        {"endpoint": "/api/orders", "downstream_service": "inventory-svc"},
        {"endpoint": "/api/users", "downstream_service": "db"},
    ])
    assert r["total"] == 2
    assert r["most_complex"] == "/api/orders"
    assert r["max_deps"] == 3
