from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cron_health import fleet_cron_health
def test_cron():
    r = fleet_cron_health([{"on_schedule": True, "last_status": "ok"}, {"on_schedule": False, "last_status": "failed"}])
    assert r["on_time"] == 1
    assert r["failed"] == 1
    assert not r["healthy"]
