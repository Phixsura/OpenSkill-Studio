from app.services.app_marketplace_app_app_api_explorer import list_endpoints

def test_all():
    r = list_endpoints()
    assert r["total"] == 8
    assert "apps" in r["tags"]

def test_filter_tag():
    r = list_endpoints(tag="apps")
    assert r["total"] == 5

def test_auth_only():
    r = list_endpoints(auth_only=True)
    assert all(e["auth"] for e in r["endpoints"])
    assert r["total"] == 7
