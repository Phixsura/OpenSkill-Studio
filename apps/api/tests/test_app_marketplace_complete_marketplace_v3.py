from app.services.app_marketplace_complete_marketplace_v3 import build_complete_marketplace_v3

def test_authenticated():
    r = build_complete_marketplace_v3(
        homepage={"stats": {"apps": 500, "developers": 100}},
        search={"query": ""}, categories={"list": []},
        app_detail={"template": True}, developer_portal={"dashboard": True},
        install_flow={"steps": []},
        user={"is_developer": True, "theme": "dark", "locale": "zh", "unread_count": 3})
    assert r["authenticated"]
    assert r["pages"]["developer_portal"] is not None
    assert r["global"]["theme"] == "dark"
    assert r["global"]["notifications"] == 3
    assert r["meta"]["total_apps"] == 500

def test_anonymous():
    r = build_complete_marketplace_v3(
        homepage={"stats": {}}, search={}, categories={},
        app_detail={}, developer_portal={}, install_flow={}, user=None)
    assert not r["authenticated"]
    assert r["pages"]["developer_portal"] is None
    assert r["global"]["theme"] == "system"

def test_non_developer():
    r = build_complete_marketplace_v3(
        homepage={}, search={}, categories={}, app_detail={},
        developer_portal={"dashboard": True}, install_flow={},
        user={"is_developer": False})
    assert r["pages"]["developer_portal"] is None
