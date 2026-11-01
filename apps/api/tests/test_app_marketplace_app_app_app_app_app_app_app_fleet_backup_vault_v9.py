from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_backup_vault_v9 import fleet_backup_vault_v9
def test_backup_v9():
    r = fleet_backup_vault_v9([{"valid": True, "size_gb": 500, "retention_days": 90}, {"valid": True, "size_gb": 300, "retention_days": 60}])
    assert r["size_gb"] == 800
    assert r["retention_compliant"]
    assert r["healthy"]
