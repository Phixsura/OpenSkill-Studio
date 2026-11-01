from app.services.app_marketplace_app_app_developer_toolkit import get_toolkit

def test_all():
    r = get_toolkit()
    assert r["total"] == 8
    assert len(r["categories"]) >= 3

def test_filter():
    r = get_toolkit(category="security")
    assert all(t["category"] == "security" for t in r["tools"])
    assert r["total"] == 2
