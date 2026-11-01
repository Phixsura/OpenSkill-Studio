from app.services.app_marketplace_platform_sprint_to_4000_7 import sprint_service_7
def test_sprint_7():
    assert sprint_service_7()["service"] == 7
    assert sprint_service_7()["target"] == 4000
