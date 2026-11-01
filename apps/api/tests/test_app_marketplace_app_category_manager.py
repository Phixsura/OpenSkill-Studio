from app.services.app_marketplace_app_category_manager import list_categories, get_category_tree, validate_category, get_category_breadcrumb

def test_list_roots():
    cats = list_categories()
    assert all(c.get("parent") is None for c in cats)
    assert len(cats) >= 6

def test_list_all():
    cats = list_categories(include_children=True)
    assert len(cats) > len(list_categories())

def test_tree():
    tree = get_category_tree()
    connector = next(t for t in tree if t["key"] == "connector")
    assert len(connector["children"]) >= 2

def test_validate():
    assert validate_category(category="connector")
    assert not validate_category(category="nonexistent")

def test_breadcrumb():
    crumbs = get_category_breadcrumb(category="slack_connector")
    assert len(crumbs) == 2
    assert crumbs[0]["key"] == "connector"
    assert crumbs[1]["key"] == "slack_connector"
