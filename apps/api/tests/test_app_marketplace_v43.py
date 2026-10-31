from app.services.app_marketplace_v43 import platform_v43
def test_v43():
    assert platform_v43()["version"] == "43.0"
