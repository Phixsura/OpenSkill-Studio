from app.services.app_marketplace_app_app_app_app_app_app_app_quick_actions import get_quick_actions, search_actions, get_categories

def test_actions():
    actions = get_quick_actions()
    assert len(actions) == 10
    ops = get_quick_actions(category="ops")
    assert len(ops) == 2

def test_search():
    r = search_actions("deploy")
    assert len(r) == 1
    assert r[0]["id"] == "deploy"
    r2 = search_actions("api")
    assert len(r2) >= 1

def test_categories():
    cats = get_categories()
    assert "ops" in cats
    assert "dev" in cats
