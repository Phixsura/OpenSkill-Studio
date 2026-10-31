from app.services.app_marketplace_category_manager import CategoryManager, Category


def test_default_categories():
    cm = CategoryManager()
    cats = cm.list_categories()
    assert len(cats) >= 8
    assert cats[0].slug == "tools"  # order=1


def test_featured_only():
    cm = CategoryManager()
    featured = cm.list_categories(featured_only=True)
    assert all(c.featured for c in featured)
    assert len(featured) >= 2


def test_add_subcategory():
    cm = CategoryManager()
    cm.add_category(Category("slack", "Slack", "Slack integrations", "💬", parent_slug="connectors"))
    children = cm.get_children("connectors")
    assert any(c.slug == "slack" for c in children)


def test_breadcrumb():
    cm = CategoryManager()
    cm.add_category(Category("sub1", "Sub", "sub", parent_slug="tools"))
    cm.add_category(Category("sub2", "SubSub", "subsub", parent_slug="sub1"))
    crumbs = cm.get_breadcrumb("sub2")
    assert [c.slug for c in crumbs] == ["tools", "sub1", "sub2"]


def test_remove_with_children_blocked():
    cm = CategoryManager()
    cm.add_category(Category("child", "Child", "c", parent_slug="tools"))
    assert cm.remove_category("tools") is False  # has children


def test_counts_and_tree():
    cm = CategoryManager()
    cm.update_count("tools", 42)
    cm.update_count("connectors", 18)
    assert cm.get_count("tools") == 42
    tree = cm.get_tree()
    tools_node = next(n for n in tree if n["slug"] == "tools")
    assert tools_node["count"] == 42
