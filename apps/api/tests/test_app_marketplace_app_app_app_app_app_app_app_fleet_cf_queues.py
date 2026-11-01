from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cf_queues import fleet_cf_queues
def test_cfq():
    r = fleet_cf_queues([{"active": True, "produced_24h": 1000000, "consumed_24h": 999000}])
    assert r["backlog"] == 1000
    assert not r["caught_up"]
