from app.services.app_marketplace_app_app_app_app_app_app_app_app_main import build_main_app_config

def test_config():
    r = build_main_app_config()
    assert r["app"]["name"] == "OpenSkill Developer Platform"
    assert len(r["features"]) == 10
    assert all(r["features"].values())
    assert len(r["routes"]) == 7
    assert r["api"]["version"] == "v1"
