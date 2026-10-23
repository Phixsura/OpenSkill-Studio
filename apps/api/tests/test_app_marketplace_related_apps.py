from app.services.app_marketplace_related_apps import find_related_by_category, find_related_by_tags, find_also_installed, build_related_section

def test_by_category():
    app = {"id": "a1", "category": "connector"}
    all_apps = [{"id": "a2", "category": "connector"}, {"id": "a3", "category": "analytics"}]
    r = find_related_by_category(app=app, all_apps=all_apps)
    assert len(r) == 1
    assert r[0]["id"] == "a2"

def test_by_tags():
    app = {"id": "a1", "tags": ["webhook", "api"]}
    all_apps = [{"id": "a2", "tags": ["webhook", "oauth"]}, {"id": "a3", "tags": ["dashboard"]}]
    r = find_related_by_tags(app=app, all_apps=all_apps)
    assert len(r) == 1

def test_also_installed():
    pairs = [{"app_a": "a1", "app_b": "a2"}, {"app_a": "a1", "app_b": "a2"}, {"app_a": "a1", "app_b": "a3"}]
    r = find_also_installed(app_id="a1", install_pairs=pairs)
    assert r[0]["app_id"] == "a2"
    assert r[0]["co_install_count"] == 2

def test_section():
    s = build_related_section(by_category=[{"id": "a2"}], by_tags=[{"id": "a3"}], also_installed=[])
    assert len(s["sections"]) == 3
