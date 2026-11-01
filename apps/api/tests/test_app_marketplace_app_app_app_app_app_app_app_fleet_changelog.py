from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_changelog import fleet_changelog
def test_changelog():
    r = fleet_changelog([{"type": "feat"}, {"type": "fix"}, {"type": "feat", "breaking": True}])
    assert r["features"] == 2
    assert r["fixes"] == 1
    assert r["breaking"] == 1
