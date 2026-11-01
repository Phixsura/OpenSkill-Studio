from app.services.app_marketplace_app_app_app_detail_sidebar import build_app_sidebar

def test_sidebar():
    app = {"version": "2.1.0", "category": "security", "size": "1.2 MB",
           "updated_at": "2026-10-23T12:00:00", "license": "MIT",
           "website": "https://example.com", "docs_url": "https://docs.example.com",
           "permissions": ["read:profile", "write:data"], "tags": ["auth", "oauth"]}
    r = build_app_sidebar(app=app)
    assert len(r["info_items"]) == 6
    assert r["info_items"][0]["value"] == "2.1.0"
    assert len(r["links"]) == 2
    assert len(r["permissions"]) == 2
    assert len(r["tags"]) == 2

def test_minimal():
    r = build_app_sidebar(app={})
    assert r["info_items"][0]["value"] == "—"
    assert len(r["links"]) == 0
    assert len(r["links"]) == 0
