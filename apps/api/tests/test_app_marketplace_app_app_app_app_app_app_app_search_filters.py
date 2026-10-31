from app.services.app_marketplace_app_app_app_app_app_app_app_search_filters import build_filters, apply_filters

def test_build():
    f = build_filters(categories=["tools"], rating_min=4, verified_only=True)
    assert f["active_count"] == 3
    assert f["has_filters"]

def test_apply():
    apps = [
        {"name": "A", "category": "tools", "rating": 4.5, "verified": True, "installs": 100},
        {"name": "B", "category": "tools", "rating": 3.0, "verified": False, "installs": 500},
        {"name": "C", "category": "analytics", "rating": 5.0, "verified": True, "installs": 200},
    ]
    f = build_filters(categories=["tools"], rating_min=4, verified_only=True)
    result = apply_filters(apps, f)
    assert len(result) == 1
    assert result[0]["name"] == "A"
