from app.services.app_marketplace_v36 import platform_v36
def test_v36():
    assert platform_v36()["version"] == "36.0"
