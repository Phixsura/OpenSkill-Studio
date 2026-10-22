"""App migration planner tests."""
import pytest
from app.services.app_migration_planner import create_migration_plan, validate_migration

V1 = {"permissions": ["read:cohorts"], "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30}}
V2 = {"permissions": ["read:cohorts", "write:cohorts"], "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60}}

def test_create_plan():
    p = create_migration_plan(from_version="1.0.0", to_version="2.0.0", old_manifest=V1, new_manifest=V2, installation_count=10)
    assert p["from_version"] == "1.0.0"
    assert p["to_version"] == "2.0.0"
    assert p["total_steps"] > 0

def test_requires_consent():
    p = create_migration_plan(from_version="1.0", to_version="2.0", old_manifest=V1, new_manifest=V2)
    assert p["requires_consent"] is True

def test_not_breaking():
    p = create_migration_plan(from_version="1.0", to_version="2.0", old_manifest=V1, new_manifest=V2)
    assert p["breaking"] is False

def test_breaking():
    p = create_migration_plan(from_version="2.0", to_version="1.0", old_manifest=V2, new_manifest=V1)
    assert p["breaking"] is True

def test_validate_safe():
    p = create_migration_plan(from_version="1.0", to_version="2.0", old_manifest=V1, new_manifest=V2)
    v = validate_migration(p)
    assert v["safe"] is True

def test_validate_large_migration():
    p = create_migration_plan(from_version="1.0", to_version="2.0", old_manifest=V1, new_manifest=V2, installation_count=500)
    v = validate_migration(p)
    assert any("Large" in w for w in v["warnings"])

def test_no_changes():
    p = create_migration_plan(from_version="1.0", to_version="1.1", old_manifest=V1, new_manifest=V1)
    assert p["requires_consent"] is False
    assert p["breaking"] is False
