from app.services.app_marketplace_complete_developer_app_list import build_developer_app_list

def test_list():
    apps = [{"name": "B", "status": "published", "install_count": 100, "updated_at": "2026-01-01"},
            {"name": "A", "status": "draft", "install_count": 0, "updated_at": "2026-06-01"}]
    r = build_developer_app_list(apps=apps, sort_by="name")
    assert r["apps"][0]["name"] == "A"
    assert r["stats"]["published"] == 1
    assert r["stats"]["draft"] == 1

def test_filter():
    apps = [{"name": "A", "status": "published"}, {"name": "B", "status": "draft"}]
    r = build_developer_app_list(apps=apps, filter_status="published")
    assert len(r["apps"]) == 1
    assert r["apps"][0]["name"] == "A"
