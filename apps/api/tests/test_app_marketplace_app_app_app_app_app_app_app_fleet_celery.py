from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_celery import fleet_celery_status
def test_cel():
    r = fleet_celery_status([{"status": "online", "active": 10, "reserved": 5}])
    assert r["active_tasks"] == 10
    assert r["all_online"]
