from app.services.app_marketplace_v63 import platform_v63
def test_v63():
    assert platform_v63()["version"] == "63.0"
