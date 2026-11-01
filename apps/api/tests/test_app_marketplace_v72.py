from app.services.app_marketplace_v72 import platform_v72
def test_v72():
    assert platform_v72()["version"] == "72.0"
