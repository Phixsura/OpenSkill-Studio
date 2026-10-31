from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ddos import fleet_ai_ddos_protection
def test_ddos():
    r = fleet_ai_ddos_protection([{"active": True, "attacks": 50, "peak_gbps": 500, "uptime_pct": 99.999}])
    assert r["attacks"] == 50
    assert r["resilient"]
