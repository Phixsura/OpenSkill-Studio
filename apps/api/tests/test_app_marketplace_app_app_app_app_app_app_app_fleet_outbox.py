from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_outbox import fleet_outbox_status
def test_outbox():
    r = fleet_outbox_status([{"pending_messages": 5, "processed_24h": 10000, "oldest_pending_min": 2},
                             {"pending_messages": 100, "processed_24h": 5000, "oldest_pending_min": 120}])
    assert r["pending"] == 105
    assert r["stuck"] == 1
    assert not r["healthy"]
