from app.services.app_marketplace_app_app_app_app_app_app_app_ep_lifecycle import EndpointLifecycle

def test_lifecycle():
    el = EndpointLifecycle()
    el.create("/api/v1/users", "v1", "team-a")
    el.activate("/api/v1/users")
    el.deprecate("/api/v1/users", "2027-06-01", "/api/v2/users")
    assert el._endpoints["/api/v1/users"]["state"] == "deprecated"
    assert el._endpoints["/api/v1/users"]["replacement"] == "/api/v2/users"
    el.sunset("/api/v1/users")
    assert len(el.by_state("sunset")) == 1

def test_stats():
    el = EndpointLifecycle()
    el.create("/a", "v1", "t1")
    el.create("/b", "v1", "t1")
    el.activate("/a")
    s = el.stats()
    assert s["by_state"]["active"] == 1
    assert s["by_state"]["draft"] == 1
