from app.services.app_marketplace_category_v2 import get_category_tree, get_category_breadcrumb, count_apps_by_category

def test_tree():
    t = get_category_tree()
    assert len(t) == 3
    connectors = next(c for c in t if c["id"] == "connectors")
    assert connectors["child_count"] == 4

def test_breadcrumb_parent():
    b = get_category_breadcrumb(category_id="connectors")
    assert len(b) == 1
    assert b[0]["label"] == "Connectors"

def test_breadcrumb_child():
    b = get_category_breadcrumb(category_id="crm")
    assert len(b) == 2
    assert b[0]["label"] == "Connectors"
    assert b[1]["label"] == "CRM"

def test_count():
    apps = [{"category": "crm"}, {"category": "crm"}, {"category": "workflows"}]
    c = count_apps_by_category(apps=apps)
    assert c["crm"] == 2
    assert c["workflows"] == 1
