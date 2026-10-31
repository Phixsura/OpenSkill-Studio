from app.services.app_marketplace_v45_319k import platform_v45
def test_v45():
    assert platform_v45()["version"] == "45.0"
    assert platform_v45()["lines"] >= 319000
