from app.services.app_marketplace_app_app_app_app_app_app_app_team_mgmt import build_team_list, can_manage

def test_team():
    r = build_team_list([
        {"name": "Alice Chen", "email": "a@t.com", "role": "owner"},
        {"name": "Bob Smith", "email": "b@t.com", "role": "developer"},
    ])
    assert r["total"] == 2
    assert r["members"][0]["avatar_initials"] == "AC"
    assert "owner" in r["by_role"]

def test_manage():
    assert can_manage("owner", "admin")
    assert can_manage("admin", "developer")
    assert not can_manage("developer", "admin")
    assert not can_manage("viewer", "viewer")
