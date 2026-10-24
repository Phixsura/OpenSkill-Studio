from app.services.app_marketplace_v35_316k import platform_v35
def test_v35():
    assert platform_v35()["version"] == "35.0"
    assert platform_v35()["lines"] >= 316000
