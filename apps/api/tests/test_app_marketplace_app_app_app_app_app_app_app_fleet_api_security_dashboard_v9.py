from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_security_dashboard_v9 import fleet_api_security_dashboard_v9
def test_asd2_v9():
    r = fleet_api_security_dashboard_v9()
    assert r["security"]["vulnerabilities"] == 0
    assert r["security"]["score"] == 98
