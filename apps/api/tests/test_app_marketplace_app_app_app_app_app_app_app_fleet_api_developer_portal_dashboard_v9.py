from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_developer_portal_dashboard_v9 import fleet_api_developer_portal_dashboard_v9
def test_adpd_v9():
    r = fleet_api_developer_portal_dashboard_v9()
    assert r["satisfaction"] == 92
    assert r["portal"]["active_developers"] == 5000
