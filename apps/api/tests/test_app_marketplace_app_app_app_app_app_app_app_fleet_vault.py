from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vault import fleet_vault_status
def test_vault():
    r = fleet_vault_status([{"sealed": False, "secret_count": 500}, {"sealed": True, "secret_count": 200}])
    assert r["sealed"] == 1
    assert r["total_secrets"] == 700
    assert not r["healthy"]
