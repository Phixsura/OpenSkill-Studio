from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ddos_v4 import fleet_ai_ddos_v4
def test_dv4():
    r = fleet_ai_ddos_v4([{"active": True, "attacks": 200, "peak_tbps": 5, "uptime_pct": 99.9999}])
    assert r["attacks"] == 200
    assert r["impenetrable"]
