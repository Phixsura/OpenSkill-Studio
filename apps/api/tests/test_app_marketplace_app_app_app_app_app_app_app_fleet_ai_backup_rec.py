from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_backup_rec import fleet_ai_backup_recovery
def test_br():
    r = fleet_ai_backup_recovery([{"active": True, "backups_24h": 48, "size_tb": 50, "rpo_min": 15, "rto_min": 30}])
    assert r["size_tb"] == 50
    assert r["resilient"]
