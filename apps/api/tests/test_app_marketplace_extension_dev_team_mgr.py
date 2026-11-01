from app.services.app_marketplace_extension_dev_team_mgr import DevTeamMgrService

def test_create_team():
    svc = DevTeamMgrService()
    team = svc.create("Core Team", "ext-1", "owner-1")
    assert len(svc.get_members(team.team_id)) == 1

def test_add_member():
    svc = DevTeamMgrService()
    team = svc.create("Team", "ext-1", "owner-1")
    assert svc.add_member(team.team_id, "dev-1", "developer", "owner-1") is True
    assert len(svc.get_members(team.team_id)) == 2

def test_role_hierarchy():
    svc = DevTeamMgrService()
    team = svc.create("Team", "ext-1", "owner-1")
    svc.add_member(team.team_id, "dev-1", "developer", "owner-1")
    # developer can't add admin
    assert svc.add_member(team.team_id, "u2", "admin", "dev-1") is False

def test_remove_member():
    svc = DevTeamMgrService()
    team = svc.create("Team", "ext-1", "owner-1")
    svc.add_member(team.team_id, "dev-1", "developer", "owner-1")
    assert svc.remove_member(team.team_id, "dev-1", "owner-1") is True
    # can't remove owner
    assert svc.remove_member(team.team_id, "owner-1", "owner-1") is False

def test_permission_check():
    svc = DevTeamMgrService()
    team = svc.create("Team", "ext-1", "owner-1")
    svc.add_member(team.team_id, "viewer-1", "viewer", "owner-1")
    assert svc.has_permission(team.team_id, "owner-1", "admin") is True
    assert svc.has_permission(team.team_id, "viewer-1", "developer") is False
