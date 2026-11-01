from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_threat_int import fleet_ai_threat_intel
def test_ti():
    r = fleet_ai_threat_intel([{"active": True, "indicators": 100000, "threats_24h": 50, "mitigated": 50}])
    assert r["indicators"] == 100000
    assert r["protected"]
