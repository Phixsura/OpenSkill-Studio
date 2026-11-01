from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ingress_ctrl_v9 import fleet_ingress_ctrl_v9
def test_ic2_v9():
    r = fleet_ingress_ctrl_v9([{"active": True, "tls_enabled": True, "rps": 50000}])
    assert r["total_rps"] == 50000
    assert r["healthy"]
