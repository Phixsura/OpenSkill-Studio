from app.services.app_marketplace_app_app_app_changelog_diff import diff_versions

def test_diff():
    old = {"version": "1.0.0", "features": ["auth", "crud"], "permissions": ["read:data"],
           "config": {"port": 3000, "debug": True}}
    new = {"version": "2.0.0", "features": ["auth", "crud", "webhooks"], "permissions": ["read:data", "write:webhooks"],
           "config": {"port": 8080, "debug": True, "region": "us"}}
    r = diff_versions(old_version=old, new_version=new)
    assert r["features_added"] == ["webhooks"]
    assert r["features_removed"] == []
    assert "write:webhooks" in r["permissions_added"]
    assert len(r["config_changes"]) == 2  # port changed, region added
    assert not r["has_breaking"]

def test_breaking():
    old = {"version": "1.0", "features": ["v1_api"], "permissions": ["admin"]}
    new = {"version": "2.0", "features": ["v2_api"], "permissions": []}
    r = diff_versions(old_version=old, new_version=new)
    assert r["has_breaking"]
    assert "v1_api" in r["features_removed"]
