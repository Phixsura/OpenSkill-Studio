from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_token_vault_v9 import fleet_token_vault_v9
def test_token_v9():
    r = fleet_token_vault_v9([{"active": True, "expired": False, "calls_today": 5000}])
    assert r["calls_today"] == 5000
    assert r["healthy"]
