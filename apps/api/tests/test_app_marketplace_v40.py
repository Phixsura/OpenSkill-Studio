from app.services.app_marketplace_v40 import platform_v40
def test_v40():
    assert platform_v40()["version"] == "40.0"
