from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_grace_shut import fleet_ai_graceful_shutdown
def test_gs():
    r = fleet_ai_graceful_shutdown([{"active": True, "shutdowns_24h": 20, "drained": 50000, "lost": 0}])
    assert r["drained"] == 50000
    assert r["zero_loss"]
