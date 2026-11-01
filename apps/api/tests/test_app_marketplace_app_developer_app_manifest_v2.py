from app.services.app_marketplace_app_developer_app_manifest_v2 import validate_manifest_v2, diff_manifests

def test_valid():
    m = {"name": "App", "version": "1.0", "entry_point": "index.ts", "permissions": ["read"]}
    r = validate_manifest_v2(manifest=m)
    assert r["valid"]

def test_missing():
    r = validate_manifest_v2(manifest={"name": "App"})
    assert not r["valid"]
    assert len(r["errors"]) >= 2

def test_bad_entry():
    m = {"name": "App", "version": "1.0", "entry_point": "index.exe", "permissions": []}
    r = validate_manifest_v2(manifest=m)
    assert not r["valid"]

def test_diff():
    old = {"name": "App", "version": "1.0", "old_field": True}
    new = {"name": "App", "version": "2.0", "new_field": True}
    d = diff_manifests(old=old, new=new)
    assert d["change_count"] == 3
    assert d["has_breaking"]  # old_field removed
