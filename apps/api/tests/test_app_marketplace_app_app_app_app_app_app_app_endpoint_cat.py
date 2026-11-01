from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_cat import EndpointCatalog

def test_register_search():
    ec = EndpointCatalog()
    ec.register("GET", "/api/users", "user-svc")
    ec.register("POST", "/api/users", "user-svc")
    ec.register("GET", "/api/orders", "order-svc")
    r = ec.search(service="user-svc")
    assert len(r) == 2
    r2 = ec.search(method="GET")
    assert len(r2) == 2

def test_stats():
    ec = EndpointCatalog()
    ec.register("GET", "/a", "s1")
    ec.register("POST", "/b", "s2")
    s = ec.stats()
    assert s["total"] == 2
    assert s["services"] == 2
