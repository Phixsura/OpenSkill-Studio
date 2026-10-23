from app.services.app_marketplace_app_app_app_app_app_app_app_svc_catalog import build_catalog, search_catalog

def test_catalog():
    services = [
        {"name": "auth-service", "tier": "critical", "owner": "platform", "status": "healthy"},
        {"name": "billing-api", "tier": "critical", "owner": "billing", "status": "healthy"},
        {"name": "email-worker", "tier": "standard", "owner": "platform", "status": "degraded"},
    ]
    r = build_catalog(services)
    assert r["total"] == 3
    assert r["healthy"] == 2
    assert r["by_tier"]["critical"] == 2
    assert r["by_owner"]["platform"] == 2

def test_search():
    services = [
        {"name": "auth-service", "description": "Authentication", "owner": "platform"},
        {"name": "billing-api", "description": "Payments", "owner": "billing"},
    ]
    assert len(search_catalog(services, "auth")) == 1
    assert len(search_catalog(services, "platform")) == 1
