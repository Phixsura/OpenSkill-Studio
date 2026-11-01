from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_breaking import fleet_breaking_changes
def test_breaking():
    r = fleet_breaking_changes([{"breaking": True, "has_migration_guide": True}, {"breaking": True, "has_migration_guide": False}, {"breaking": False}])
    assert r["breaking"] == 2
    assert r["with_guide"] == 1
    assert not r["safe"]
