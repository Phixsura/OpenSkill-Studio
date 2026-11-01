from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dr_v5 import fleet_ai_dr_v5
def test_dv5():
    r = fleet_ai_dr_v5([{"active": True, "rto_s": 30, "rpo_s": 5, "drills_30d": 8, "regions": 10}])
    assert r["rto_s"] == 30
    assert r["instant"]
