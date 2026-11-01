from app.services.app_marketplace_app_app_app_app_app_app_app_registry_final import registry_summary, search_registry

def test_summary():
    r = registry_summary([
        {"name": "auth-svc", "module": "security", "status": "active"},
        {"name": "user-svc", "module": "core", "status": "active"},
        {"name": "legacy-svc", "module": "core", "status": "deprecated"},
    ])
    assert r["total_services"] == 3
    assert r["modules"] == 2
    assert r["active"] == 2
    assert not r["all_active"]

def test_search():
    svcs = [{"name": "auth-svc", "module": "security"}, {"name": "user-svc", "module": "core"},
            {"name": "auth-api", "module": "security"}]
    r = search_registry(svcs, query="auth")
    assert len(r) == 2
    r2 = search_registry(svcs, module="core")
    assert len(r2) == 1
