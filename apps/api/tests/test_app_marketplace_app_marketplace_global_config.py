from app.services.app_marketplace_app_marketplace_global_config import get_config, get_all_config, get_public_config

def test_get():
    assert get_config(key="platform_name") == "OpenSkill Marketplace"

def test_default():
    assert get_config(key="nonexistent", default="fallback") == "fallback"

def test_all():
    c = get_all_config()
    assert len(c) >= 10

def test_public():
    p = get_public_config()
    assert "platform_name" in p
    assert "support_email" not in p  # not public
    assert "api_base_url" not in p
