from app.services.app_marketplace_app_app_app_app_app_app_app_ep_inventory import EndpointInventory

def test_inventory():
    ei = EndpointInventory()
    ei.add("GET", "/api/v1/users", "user-svc")
    ei.add("POST", "/api/v1/users", "user-svc")
    ei.add("GET", "/api/v1/orders", "order-svc")
    ei.add("GET", "/api/v0/legacy", "legacy-svc", deprecated=True)
    r = ei.search(service="user-svc")
    assert len(r) == 2
    r2 = ei.search(include_deprecated=True)
    assert len(r2) == 4
    s = ei.stats()
    assert s["deprecated"] == 1
    assert s["services"] == 3
