from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_http_metrics_v9 import fleet_http_metrics_v9
def test_hm_v9():
    r = fleet_http_metrics_v9([{"2xx": 9900, "3xx": 50, "4xx": 40, "5xx": 10}])
    assert r["2xx"] == 9900
    assert r["healthy"]
