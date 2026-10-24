from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_django import fleet_django_status
def test_dj():
    r = fleet_django_status([{"running": True, "views": 300, "pending_migrations": 0}])
    assert r["views"] == 300
    assert r["up_to_date"]
