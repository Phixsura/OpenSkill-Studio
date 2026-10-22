from app.services.app_developer_app_api_keys_page_builder import build_api_keys_page

def test_page():
    p = build_api_keys_page(keys=[{"name": "prod", "revoked": False}, {"name": "old", "revoked": True}])
    assert p["active_count"] == 1
    assert p["can_create"] is True
