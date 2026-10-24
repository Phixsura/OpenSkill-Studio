from app.services.app_marketplace_v51 import platform_v51
def test_v51():
    assert platform_v51()["version"] == "51.0"
