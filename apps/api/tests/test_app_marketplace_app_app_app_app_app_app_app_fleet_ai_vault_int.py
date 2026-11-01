from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_vault_int import fleet_ai_vault_integration
def test_vi():
    r = fleet_ai_vault_integration([{"active": True, "secrets": 2000, "accesses_24h": 5000000, "rotations": 100}])
    assert r["secrets"] == 2000
    assert r["sealed"]
