from app.services.app_developer_app_secrets_page_builder import build_secrets_page

def test_page():
    p = build_secrets_page(secrets=[{"key": "API_KEY"}, {"key": "SECRET"}])
    assert p["count"] == 2
    assert p["can_add"] is True
    assert p["remaining"] == 18
