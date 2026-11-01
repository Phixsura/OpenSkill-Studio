from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_env_promoter_v9 import fleet_env_promoter_v9
def test_ep_v9():
    r = fleet_env_promoter_v9([{"status": "promoted"}, {"status": "promoted"}])
    assert r["promoted"] == 2
    assert r["blocked"] == 0
    assert r["healthy"]
