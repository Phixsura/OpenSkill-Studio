"""Manifest merger tests."""
from app.services.app_manifest_merger import merge_manifests, patch_manifest

def test_simple_merge():
    base = {"app": {"name": "Old"}, "permissions": ["read:cohorts"]}
    updates = {"app": {"name": "New"}}
    result = merge_manifests(base, updates)
    assert result["app"]["name"] == "New"
    assert result["permissions"] == ["read:cohorts"]

def test_deep_merge():
    base = {"sandbox": {"runtime": "python3.12", "memory_mb": 128}}
    updates = {"sandbox": {"memory_mb": 256}}
    result = merge_manifests(base, updates)
    assert result["sandbox"]["runtime"] == "python3.12"
    assert result["sandbox"]["memory_mb"] == 256

def test_list_replace():
    base = {"permissions": ["read:cohorts"]}
    updates = {"permissions": ["read:cohorts", "write:cohorts"]}
    result = merge_manifests(base, updates)
    assert len(result["permissions"]) == 2

def test_no_mutation():
    base = {"app": {"name": "X"}}
    merge_manifests(base, {"app": {"name": "Y"}})
    assert base["app"]["name"] == "X"

def test_patch_set():
    m = {"app": {"name": "Old"}}
    result = patch_manifest(m, [{"op": "set", "path": "app.name", "value": "New"}])
    assert result["app"]["name"] == "New"

def test_patch_delete():
    m = {"app": {"name": "X", "desc": "Y"}}
    result = patch_manifest(m, [{"op": "delete", "path": "app.desc"}])
    assert "desc" not in result["app"]

def test_patch_append():
    m = {"permissions": ["read:cohorts"]}
    result = patch_manifest(m, [{"op": "append", "path": "permissions", "value": "write:cohorts"}])
    assert "write:cohorts" in result["permissions"]

def test_multiple_patches():
    m = {"app": {"name": "X", "version": "1.0.0"}, "permissions": []}
    result = patch_manifest(m, [
        {"op": "set", "path": "app.version", "value": "2.0.0"},
        {"op": "append", "path": "permissions", "value": "read:cohorts"},
    ])
    assert result["app"]["version"] == "2.0.0"
    assert "read:cohorts" in result["permissions"]
