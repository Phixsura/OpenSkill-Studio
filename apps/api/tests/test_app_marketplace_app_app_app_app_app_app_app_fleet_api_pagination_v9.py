from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_pagination_v9 import fleet_api_pagination_v9
def test_apag_v9():
    r = fleet_api_pagination_v9([{"strategy": "cursor"}, {"strategy": "keyset"}])
    assert r["cursor"] == 1
    assert r["keyset"] == 1
    assert r["healthy"]
