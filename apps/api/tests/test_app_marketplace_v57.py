from app.services.app_marketplace_v57 import platform_v57
def test_v57():
    assert platform_v57()["version"] == "57.0"
