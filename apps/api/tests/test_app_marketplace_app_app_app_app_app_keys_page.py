from app.services.app_marketplace_app_app_app_app_app_keys_page import build_keys_page, create_app_key

def test_page():
    keys = [
        {"prefix": "osk_abc", "name": "Prod", "scopes": ["read"], "revoked": False, "requests_30d": 5000},
        {"prefix": "osk_def", "name": "Old", "scopes": [], "revoked": True, "requests_30d": 0},
    ]
    r = build_keys_page(app_name="SuperApp", keys=keys)
    assert r["active"] == 1
    assert r["total_requests_30d"] == 5000
    assert r["can_create"]

def test_create():
    r = create_app_key(app_id="a1", name="Test Key", scopes=["read", "write"])
    assert r["key"].startswith("osk_")
    assert r["name"] == "Test Key"
