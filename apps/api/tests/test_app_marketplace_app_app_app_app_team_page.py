from app.services.app_marketplace_app_app_app_app_team_page import build_team_page

def test_team():
    members = [
        {"id": "u1", "name": "Alice", "email": "a@b.com", "role": "owner"},
        {"id": "u2", "name": "Bob", "email": "b@b.com", "role": "editor"},
    ]
    invites = [{"email": "charlie@b.com", "role": "viewer", "sent_at": "2026-01-01"}]
    r = build_team_page(org_name="Acme", members=members, pending_invites=invites)
    assert r["total_members"] == 2
    assert r["pending_count"] == 1
    assert r["members"][0]["role"] == "owner"
    assert r["by_role"]["owner"] == 1
