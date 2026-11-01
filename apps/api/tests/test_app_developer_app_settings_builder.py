from app.services.app_developer_app_settings_builder import build_app_settings

def test_settings():
    s = build_app_settings({"name": "X", "slug": "x", "category": "connector", "status": "draft", "oauth_client_id": "osk_123"})
    assert s["general"]["name"] == "X"
    assert s["oauth"]["client_id"] == "osk_123"
    assert s["danger_zone"]["can_delete"] is True

def test_published():
    s = build_app_settings({"status": "published"})
    assert s["danger_zone"]["can_delete"] is False
    assert s["danger_zone"]["can_archive"] is True
