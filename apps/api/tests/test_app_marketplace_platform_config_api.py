from app.services.app_marketplace_platform_config_api import get_platform_config

def test_config():
    r = get_platform_config()
    assert r["status"] == "operational"
    assert r["features"]["marketplace"]
    assert r["platform_name"] == "OpenSkill Marketplace"
