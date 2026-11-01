from app.services.app_marketplace_app_app_app_app_app_app_app_store_listing import build_listing, validate_listing

def test_build():
    r = build_listing("My App", "Best app ever", "A" * 60, "productivity",
                        screenshots=4, features=["auth", "api", "webhooks"])
    assert r["completeness_pct"] == 100
    assert r["ready_to_publish"]

def test_incomplete():
    r = build_listing("My App", "", "Short", "tools")
    assert r["completeness_pct"] < 80
    assert not r["ready_to_publish"]

def test_validate():
    listing = build_listing("App", "Tag", "x" * 60, "cat", screenshots=2)
    r = validate_listing(listing)
    assert r["valid"]
    r2 = validate_listing(build_listing("", "", "short", "cat"))
    assert not r2["valid"]
    assert r2["issue_count"] >= 2
