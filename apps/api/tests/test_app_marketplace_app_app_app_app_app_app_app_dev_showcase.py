from app.services.app_marketplace_app_app_app_app_app_app_app_dev_showcase import build_showcase

def test_showcase():
    r = build_showcase([
        {"name": "Acme Corp", "app_count": 10, "total_installs": 100000, "verified": True, "spotlight": True},
        {"name": "Indie Dev", "app_count": 2, "total_installs": 5000, "verified": False},
        {"name": "Big Tech", "app_count": 15, "total_installs": 200000, "verified": True, "spotlight": True},
    ])
    assert r["total"] == 3
    assert r["spotlights"] == 2
    assert r["developers"][0]["name"] == "Big Tech"  # highest ranked
