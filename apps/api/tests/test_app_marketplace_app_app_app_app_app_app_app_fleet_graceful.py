from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_graceful import fleet_graceful_shutdown
def test_graceful():
    r = fleet_graceful_shutdown([{"graceful_shutdown": True}, {"graceful_shutdown": False}])
    assert r["forced_kill"] == 1
    assert not r["compliant"]
