from app.services.app_marketplace_extension_category_mgr import ExtCategoryMgrService

def test_seeded():
    svc = ExtCategoryMgrService()
    assert len(svc.get_all()) >= 6

def test_create_child():
    svc = ExtCategoryMgrService()
    svc.create("linters", "Linters", "linters", parent_id="dev-tools", icon="🔍")
    tree = svc.get_tree()
    dev_tools = next(t for t in tree if t["category"].category_id == "dev-tools")
    assert len(dev_tools["children"]) == 1

def test_slug_lookup():
    svc = ExtCategoryMgrService()
    c = svc.get_by_slug("analytics")
    assert c is not None and c.icon == "📊"

def test_count():
    svc = ExtCategoryMgrService()
    svc.increment_count("ui")
    assert svc._categories["ui"].extension_count == 1
