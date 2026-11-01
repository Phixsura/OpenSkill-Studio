from app.services.app_marketplace_app_app_app_app_app_list_page import build_app_list_page

def test_list():
    apps = [
        {"id": "a1", "name": "Zebra", "status": "active", "installs": 100, "created_at": "2026-01-01"},
        {"id": "a2", "name": "Alpha", "status": "draft", "installs": 0, "created_at": "2026-03-01"},
    ]
    r = build_app_list_page(apps=apps, sort_by="newest")
    assert r["total"] == 2
    assert r["apps"][0]["name"] == "Alpha"  # newest first
    assert r["has_draft"]

def test_sort_name():
    apps = [{"name": "Zebra"}, {"name": "Alpha"}]
    r = build_app_list_page(apps=apps, sort_by="name")
    assert r["apps"][0]["name"] == "Alpha"
