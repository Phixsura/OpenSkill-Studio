from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_bak_v2 import fleet_ai_platform_backup_v2
def test_pbv2():
    r = fleet_ai_platform_backup_v2([{"active": True, "backups_24h": 96, "size_tb": 1000, "rpo_min": 5, "verified": True}])
    assert r["size_tb"] == 1000
    assert r["protected"]
