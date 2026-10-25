from app.services.app_marketplace_platform_sprint_to_4000_6 import sprint_service_6
def test_sprint_6():
    assert sprint_service_6()["service"] == 6
    assert sprint_service_6()["target"] == 4000
