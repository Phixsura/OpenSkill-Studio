from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_pinjection import fleet_ai_pinjection
def test_pi():
    r = fleet_ai_pinjection([{"active": True, "scanned_24h": 10000000, "blocked_24h": 5000}])
    assert r["block_rate"] == 0.05
