from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tls_mgr import fleet_ai_tls_manager
def test_tls():
    r = fleet_ai_tls_manager([{"active": True, "certs": 500, "expiring_30d": 0, "auto_renewed": 100}])
    assert r["certs"] == 500
    assert r["healthy"]
