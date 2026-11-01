from app.services.app_marketplace_extension_endpoint_registry import EndpointRegistryService


def test_register():
    svc = EndpointRegistryService()
    ep = svc.register("/users", "GET", "v1", "ext-1", "list_users", "List users")
    assert ep.method == "GET"
    assert ep.handler == "list_users"


def test_record_calls():
    svc = EndpointRegistryService()
    svc.register("/users", "GET", "v1", "ext-1", "h")
    svc.record_call("GET", "/users", "v1", 50)
    svc.record_call("GET", "/users", "v1", 100)
    eps = svc.discover(extension_id="ext-1")
    assert eps[0].call_count == 2
    assert eps[0].avg_latency_ms == 75.0


def test_deprecate():
    svc = EndpointRegistryService()
    svc.register("/old", "GET", "v1", "ext-1", "h")
    svc.deprecate("GET", "/old", "v1")
    eps = svc.discover()
    assert len(eps) == 0  # hidden by default
    eps_all = svc.discover(include_deprecated=True)
    assert len(eps_all) == 1


def test_discover_by_tag():
    svc = EndpointRegistryService()
    svc.register("/a", "GET", "v1", "ext-1", "h", tags=["users"])
    svc.register("/b", "POST", "v1", "ext-1", "h", tags=["admin"])
    assert len(svc.discover(tag="users")) == 1


def test_discover_by_version():
    svc = EndpointRegistryService()
    svc.register("/a", "GET", "v1", "ext-1", "h")
    svc.register("/b", "GET", "v2", "ext-1", "h")
    assert len(svc.discover(version="v2")) == 1


def test_most_used():
    svc = EndpointRegistryService()
    svc.register("/hot", "GET", "v1", "ext-1", "h")
    svc.register("/cold", "GET", "v1", "ext-2", "h")
    for _ in range(10):
        svc.record_call("GET", "/hot", "v1", 20)
    svc.record_call("GET", "/cold", "v1", 20)
    top = svc.get_most_used(1)
    assert top[0].path == "/hot"


def test_slowest():
    svc = EndpointRegistryService()
    svc.register("/fast", "GET", "v1", "ext-1", "h")
    svc.register("/slow", "GET", "v1", "ext-2", "h")
    svc.record_call("GET", "/fast", "v1", 10)
    svc.record_call("GET", "/slow", "v1", 5000)
    slow = svc.get_slowest(1)
    assert slow[0].path == "/slow"


def test_stats():
    svc = EndpointRegistryService()
    svc.register("/a", "GET", "v1", "ext-1", "h")
    svc.register("/b", "POST", "v2", "ext-2", "h")
    svc.deprecate("GET", "/a", "v1")
    stats = svc.get_stats()
    assert stats["total"] == 2
    assert stats["deprecated"] == 1
    assert stats["extensions"] == 2
    assert stats["versions"] == ["v1", "v2"]
