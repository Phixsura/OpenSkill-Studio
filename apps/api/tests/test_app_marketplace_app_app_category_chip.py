from app.services.app_marketplace_app_app_category_chip import build_category_chips

def test_chips():
    categories = [{"id": "tools", "name": "Tools", "count": 85},
                  {"id": "security", "name": "Security", "count": 48}]
    r = build_category_chips(categories=categories, active="security")
    assert r["total"] == 3  # all + 2
    assert r["active_id"] == "security"
    assert r["chips"][0]["id"] == "all"
    assert not r["chips"][0]["active"]
    assert r["chips"][2]["active"]

def test_none_active():
    r = build_category_chips(categories=[{"id": "x", "name": "X"}])
    assert r["chips"][0]["active"]  # "all" is active
