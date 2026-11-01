from app.services.app_marketplace_platform_sprint_to_4000_1 import sprint_service_1
def test_sprint_1():
    assert sprint_service_1()["service"] == 1
    assert sprint_service_1()["target"] == 4000
