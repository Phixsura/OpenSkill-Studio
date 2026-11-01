from app.services.app_marketplace_v39 import platform_v39
def test_v39():
    assert platform_v39()["version"] == "39.0"
