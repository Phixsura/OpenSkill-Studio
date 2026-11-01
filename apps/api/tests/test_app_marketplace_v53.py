from app.services.app_marketplace_v53 import platform_v53
def test_v53():
    assert platform_v53()["version"] == "53.0"
