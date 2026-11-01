from app.services.app_marketplace_app_app_app_team_management import build_team_page

def test_team():
    members = [
        {"id": "u1", "name": "Alice", "email": "a@b.com", "role": "owner"},
        {"id": "u2", "name": "Bob", "email": "b@b.com", "role": "editor"},
        {"id": "u3", "name": "Charlie", "email": "c@b.com", "role": "viewer"},
    ]
    r = build_team_page(members=members, pending_invites=2, max_members=10)
    assert r["total"] == 3
    assert r["members"][0]["role"] == "owner"  # sorted by level
    assert r["pending_invites"] == 2
    assert r["seats_remaining"] == 7
    assert r["can_invite"]

def test_full():
    members = [{"id": f"u{i}", "name": f"User {i}", "role": "viewer"} for i in range(5)]
    r = build_team_page(members=members, max_members=5)
    assert not r["can_invite"]
    assert r["seats_remaining"] == 0
