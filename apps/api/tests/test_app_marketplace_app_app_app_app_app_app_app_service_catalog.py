from app.services.app_marketplace_app_app_app_app_app_app_app_service_catalog import ServiceCatalog

def test_catalog():
    c = ServiceCatalog()
    c.register("auth", name="Auth Service", team="platform", tier="tier0", dependencies=[])
    c.register("api", name="API Gateway", team="platform", tier="tier0", dependencies=["auth"])
    c.register("billing", name="Billing", team="commerce", tier="tier1", dependencies=["auth", "api"])
    assert len(c.search(team="platform")) == 2
    assert len(c.search(tier="tier0")) == 2
    assert len(c.search(query="billing")) == 1
    deps = c.dependency_map("billing")
    assert deps["count"] == 2
    s = c.stats()
    assert s["total"] == 3
    assert s["by_team"]["platform"] == 2
