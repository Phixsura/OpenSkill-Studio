from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_err_class import fleet_error_classification
def test_classify():
    r = fleet_error_classification([{"status_code": 404}, {"status_code": 500}, {"status_code": 429}, {"status_code": 503}])
    assert r["client_errors"] == 2
    assert r["server_errors"] == 2
