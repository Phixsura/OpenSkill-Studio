from app.services.app_marketplace_platform_sprint_to_4000_3 import sprint_service_3
def test_sprint_3():
    assert sprint_service_3()["service"] == 3
    assert sprint_service_3()["target"] == 4000
