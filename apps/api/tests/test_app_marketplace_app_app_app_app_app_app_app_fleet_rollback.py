from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rollback import fleet_rollback_stats
def test_rollback():
    r = fleet_rollback_stats([{"type": "auto"}, {"type": "manual"}, {"type": "auto"}])
    assert r["auto"] == 2
    assert r["manual"] == 1
    assert r["total"] == 3
