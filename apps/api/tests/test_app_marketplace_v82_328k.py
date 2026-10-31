from app.services.app_marketplace_v82_328k import platform_v82
def test_v82():
    assert platform_v82()["version"] == "82.0"
    assert platform_v82()["lines"] >= 328000
