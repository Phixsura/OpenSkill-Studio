from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_err_corr import fleet_error_correlation
def test_corr():
    r = fleet_error_correlation([{"service": "a"}, {"service": "a"}, {"service": "b"}, {"service": "c"}, {"service": "d"}])
    assert r["hotspot"] == "a"
    assert r["cascading"]
