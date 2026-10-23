from app.services.app_marketplace_changelog_comparison_v2 import compare_versions_v2, build_migration_notes

def test_compare():
    a = {"version": "1.0", "changes": [{"description": "Feature A"}], "permissions": ["read"]}
    b = {"version": "2.0", "changes": [{"description": "Feature A"}, {"description": "Feature B"}], "permissions": ["read", "write"]}
    r = compare_versions_v2(version_a=a, version_b=b)
    assert r["total_differences"] == 2  # 1 new change + 1 new permission
    assert "write" in r["permissions_added"]
    assert len(r["common"]) == 1

def test_breaking():
    a = {"version": "1.0", "permissions": ["read", "admin"]}
    b = {"version": "2.0", "permissions": ["read"]}
    r = compare_versions_v2(version_a=a, version_b=b)
    assert r["has_breaking"]
    assert "admin" in r["permissions_removed"]

def test_notes_safe():
    comp = {"permissions_removed": [], "permissions_added": [], "has_breaking": False}
    notes = build_migration_notes(comparison=comp)
    assert any("Safe" in n for n in notes)

def test_notes_breaking():
    comp = {"permissions_removed": ["admin"], "permissions_added": ["write"], "has_breaking": True}
    notes = build_migration_notes(comparison=comp)
    assert len(notes) == 3
