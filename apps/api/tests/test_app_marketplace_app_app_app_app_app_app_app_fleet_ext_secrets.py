from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ext_secrets import fleet_external_secrets
def test_eso():
    r = fleet_external_secrets([{"synced": True}, {"synced": True}, {"status": "SecretSyncedError"}])
    assert r["synced"] == 3
    assert r["failed"] == 1
    assert not r["healthy"]
