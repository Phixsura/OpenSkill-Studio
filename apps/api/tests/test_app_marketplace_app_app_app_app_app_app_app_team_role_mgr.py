from app.services.app_marketplace_app_app_app_app_app_app_app_team_role_mgr import (
    add_member, check_access, change_role, clear_members,
)

def test_add_and_check():
    clear_members()
    add_member("u1", "owner", "system")
    add_member("u2", "developer", "u1")
    assert check_access("u1", "anything")  # owner has *
    assert check_access("u2", "deploy")
    assert not check_access("u2", "manage_members")
    assert not check_access("u99", "view")  # not member
    clear_members()

def test_change_role():
    clear_members()
    add_member("u1", "owner", "system")
    add_member("u2", "viewer", "u1")
    r = change_role("u2", "developer", "u1")
    assert r["changed"]
    assert check_access("u2", "deploy")
    clear_members()
