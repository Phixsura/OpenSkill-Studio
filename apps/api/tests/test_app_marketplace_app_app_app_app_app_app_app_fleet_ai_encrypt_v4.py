from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_encrypt_v4 import fleet_ai_encryption_v4
def test_ev4():
    r = fleet_ai_encryption_v4([{"active": True, "data_tb": 5000, "keys": 10000, "rotations": 500, "at_rest": True, "in_transit": True}])
    assert r["data_tb"] == 5000
    assert r["e2e"]
