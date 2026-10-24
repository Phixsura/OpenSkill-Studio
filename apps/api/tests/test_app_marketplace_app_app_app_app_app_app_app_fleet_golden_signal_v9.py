from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_golden_signal_v9 import fleet_golden_signal_v9
def test_gs_v9():
    r = fleet_golden_signal_v9([{"latency_ok": True, "traffic_ok": True, "errors_ok": True, "saturation_ok": True}])
    assert r["latency_ok"] == 1
    assert r["healthy"]
