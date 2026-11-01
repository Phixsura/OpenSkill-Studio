from app.services.app_marketplace_v74 import platform_v74
def test_v74():
    assert platform_v74()["version"] == "74.0"
