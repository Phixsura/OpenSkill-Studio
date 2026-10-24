from app.services.app_marketplace_app_app_app_manifest import validate_manifest, build_manifest

def test_valid():
    m = {"name": "my-cool-app", "version": "1.0.0", "description": "A cool app", "author": "Alice"}
    r = validate_manifest(manifest=m)
    assert r["valid"]

def test_missing_fields():
    r = validate_manifest(manifest={})
    assert not r["valid"]
    assert len(r["errors"]) >= 4

def test_bad_name():
    r = validate_manifest(manifest={"name": "BAD NAME!", "version": "1.0.0", "description": "x", "author": "x"})
    assert not r["valid"]

def test_build():
    r = build_manifest(name="my-app", version="2.0.0", description="Great app", author="Bob",
                       permissions=["read:apps"])
    assert r["name"] == "my-app"
    assert r["permissions"] == ["read:apps"]
