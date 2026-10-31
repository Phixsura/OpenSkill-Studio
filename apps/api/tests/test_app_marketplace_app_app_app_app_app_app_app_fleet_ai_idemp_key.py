from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_idemp_key import fleet_ai_idempotency_key
def test_ik():
    r = fleet_ai_idempotency_key([{"active": True, "keys": 1000000, "prevented": 50000, "ttl_s": 3600}])
    assert r["keys"] == 1000000
    assert r["protecting"]
