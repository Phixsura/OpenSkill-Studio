from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_threat_intel_v9 import fleet_threat_intel_v9
def test_ti2_v9():
    r = fleet_threat_intel_v9([{"active": True, "iocs_today": 500, "blocked_today": 50}])
    assert r["iocs_today"] == 500
    assert r["healthy"]
