from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lightstep import fleet_lightstep_status
def test_ls():
    r = fleet_lightstep_status([{"instrumented": True}, {"instrumented": True, "latency_regression": True}, {"instrumented": False}])
    assert r["instrumented"] == 2
    assert r["latency_regressions"] == 1
    assert r["coverage_pct"] == 66.7
