from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_dev_experience_v9 import fleet_api_dev_experience_v9
def test_adx_v9():
    r = fleet_api_dev_experience_v9([{"satisfaction": 92, "time_to_first_hello_min": 5, "doc_coverage_pct": 95}])
    assert r["avg_satisfaction"] == 92.0
    assert r["healthy"]
