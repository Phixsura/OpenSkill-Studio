from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_changelog_v9 import fleet_api_changelog_v9
def test_acl_v9():
    r = fleet_api_changelog_v9([{"has_changelog": True, "changelog_entries": 50, "breaking_changes": 0}])
    assert r["with_changelog"] == 1
    assert r["healthy"]
