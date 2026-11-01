from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nats import fleet_nats_status
def test_nats():
    r = fleet_nats_status([{"connected": True, "subscriptions": 1000, "msgs_per_sec": 50000}])
    assert r["subscriptions"] == 1000
    assert r["msgs_per_sec"] == 50000
    assert r["healthy"]
