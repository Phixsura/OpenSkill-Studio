from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_devsecops_v7 import fleet_ai_devsecops_v7
def test_dsov7():
    r = fleet_ai_devsecops_v7([{"active": True, "scans": 10000, "vulns": 50, "fixed": 50, "sast_pct": 100}])
    assert r["scans"] == 10000
    assert r["secure"]
