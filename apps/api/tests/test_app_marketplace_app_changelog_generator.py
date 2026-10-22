from app.services.app_marketplace_app_changelog_generator import auto_generate_changelog

def test_initial():
    cl = auto_generate_changelog(old_manifest=None, new_manifest={}, version="1.0.0")
    assert "Initial release" in cl

def test_with_changes():
    old = {"permissions": ["read:cohorts"]}
    new = {"permissions": ["read:cohorts", "write:cohorts"]}
    cl = auto_generate_changelog(old_manifest=old, new_manifest=new, version="2.0.0")
    assert "write:cohorts" in cl

def test_no_changes():
    cl = auto_generate_changelog(old_manifest={"permissions": ["read:cohorts"]}, new_manifest={"permissions": ["read:cohorts"]}, version="1.1")
    assert "Minor" in cl
