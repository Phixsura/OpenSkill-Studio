from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_err_tax import fleet_error_taxonomy
def test_tax():
    r = fleet_error_taxonomy([{"root_cause": "timeout"}, {"root_cause": "timeout"}, {"root_cause": "oom"}])
    assert r["top_cause"] == "timeout"
    assert r["causes"] == 2
