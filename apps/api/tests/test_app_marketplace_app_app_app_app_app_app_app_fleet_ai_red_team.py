from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_red_team import fleet_ai_red_teaming
def test_rt():
    r = fleet_ai_red_teaming([{"active": True, "attacks_24h": 10000, "vulns_found": 20, "fixed": 20}])
    assert r["vulns"] == 20
    assert r["hardened"]
