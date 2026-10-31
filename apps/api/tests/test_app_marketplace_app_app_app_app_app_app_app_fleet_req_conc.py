from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_req_conc import fleet_request_concurrency
def test_conc():
    r = fleet_request_concurrency([{"concurrent": 80, "max_concurrent": 100}, {"concurrent": 90, "max_concurrent": 100}])
    assert r["total_concurrent"] == 170
    assert r["util_pct"] == 85.0
    assert r["pressure"]
