from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_quality_metrics_v9 import fleet_api_quality_metrics_v9
def test_aqm2_v9():
    r = fleet_api_quality_metrics_v9()
    assert r["grade"] == "A+"
    assert r["overall_score"] == 97
