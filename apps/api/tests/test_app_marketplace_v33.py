from app.services.app_marketplace_v33 import platform_v33
def test_v33():
    assert platform_v33()["version"] == "33.0"
