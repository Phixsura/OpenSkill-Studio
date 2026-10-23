from app.services.app_marketplace_app_multitenancy_router import resolve_tenant, list_tenant_strategies

def test_subdomain():
    r = resolve_tenant(host="acme.marketplace.openskill.dev", path="/api/apps")
    assert r["resolved"]
    assert r["tenant_id"] == "acme"
    assert r["strategy"] == "subdomain"

def test_path():
    r = resolve_tenant(host="openskill.dev", path="/t/acme/api/apps")
    assert r["resolved"]
    assert r["tenant_id"] == "acme"
    assert r["strategy"] == "path"

def test_header():
    r = resolve_tenant(host="openskill.dev", path="/api", header_tenant="acme")
    assert r["tenant_id"] == "acme"
    assert r["strategy"] == "header"

def test_unresolved():
    r = resolve_tenant(host="openskill.dev", path="/api")
    assert not r["resolved"]

def test_strategies():
    r = list_tenant_strategies()
    assert len(r["strategies"]) == 3
