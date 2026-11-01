from app.services.app_marketplace_v30 import platform_v30
def test_v30():
    assert platform_v30()["version"] == "30.0"
