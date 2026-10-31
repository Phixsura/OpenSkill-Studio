from app.services.app_marketplace_v65 import platform_v65
def test_v65():
    assert platform_v65()["version"] == "65.0"
