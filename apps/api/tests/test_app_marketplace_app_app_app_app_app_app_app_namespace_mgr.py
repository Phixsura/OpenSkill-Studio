from app.services.app_marketplace_app_app_app_app_app_app_app_namespace_mgr import NamespaceManager

def test_create_list():
    nm = NamespaceManager()
    nm.create("acme-prod", "acme", {"env": "prod"})
    nm.create("acme-staging", "acme", {"env": "staging"})
    nm.create("beta-prod", "beta")
    assert len(nm.list_by_tenant("acme")) == 2
    assert nm.stats()["tenants"] == 2

def test_delete():
    nm = NamespaceManager()
    nm.create("test", "t1")
    nm.delete("test")
    assert nm.stats()["total"] == 0
