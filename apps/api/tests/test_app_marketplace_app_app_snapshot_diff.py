from app.services.app_marketplace_app_app_snapshot_diff import diff_snapshots

def test_diff():
    before = {"port": 3000, "debug": False, "name": "App"}
    after = {"port": 8080, "debug": False, "region": "us-east"}
    r = diff_snapshots(before=before, after=after)
    assert r["changed_count"] == 1
    assert r["changed"]["port"]["before"] == 3000
    assert r["added_count"] == 1
    assert "region" in r["added"]
    assert r["removed_count"] == 1
    assert "name" in r["removed"]
    assert r["has_drift"]

def test_no_drift():
    r = diff_snapshots(before={"a": 1}, after={"a": 1})
    assert not r["has_drift"]
