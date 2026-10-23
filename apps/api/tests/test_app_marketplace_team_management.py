from app.services.app_marketplace_team_management import invite_member, update_member_role, get_team_summary

def test_invite():
    r = invite_member(team_id="t1", email="dev@test.com", role="developer", invited_by="u1")
    assert r["status"] == "pending"

def test_invalid_role():
    r = invite_member(team_id="t1", email="x", role="superadmin", invited_by="u1")
    assert r["error"]

def test_update_role():
    r = update_member_role(member_id="m1", new_role="admin", updated_by="u1")
    assert r["role"] == "admin"

def test_cant_assign_owner():
    r = update_member_role(member_id="m1", new_role="owner", updated_by="u1")
    assert r["error"]

def test_summary():
    members = [{"role": "owner", "status": "active"}, {"role": "developer", "status": "active"},
               {"role": "developer", "status": "pending"}]
    s = get_team_summary(members=members)
    assert s["active"] == 2
    assert s["pending"] == 1
    assert s["by_role"]["developer"] == 2
