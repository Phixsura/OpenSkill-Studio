from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_performance_dashboard_v9 import fleet_api_performance_dashboard_v9
def test_apd2_v9():
    r = fleet_api_performance_dashboard_v9()
    assert r["within_sla"]
    assert r["performance"]["p99_ms"] == 80
