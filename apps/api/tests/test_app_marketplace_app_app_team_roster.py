from app.services.app_marketplace_app_app_team_roster import build_team_roster

def test_roster():
    members = [
        {"id": "1", "name": "Alice", "email": "a@b.com", "role": "owner"},
        {"id": "2", "name": "Bob", "email": "b@b.com", "role": "editor"},
        {"id": "3", "name": "Charlie", "email": "c@b.com", "role": "viewer", "active": False},
    ]
    r = build_team_roster(members=members)
    assert r["total"] == 3
    assert r["active"] == 2
    assert r["members"][0]["role"] == "owner"  # sorted by role level
    assert r["by_role"]["owner"] == 1
