from app.services.app_marketplace_app_app_team_invite import send_invite, build_pending_invites

def test_send():
    r = send_invite(email="alice@example.com", role="editor", org_name="Acme", inviter="Bob")
    assert r["invite_id"].startswith("inv_")
    assert r["status"] == "pending"

def test_invalid_email():
    r = send_invite(email="bad", role="editor", org_name="X", inviter="Y")
    assert "error" in r

def test_invalid_role():
    r = send_invite(email="a@b.com", role="superadmin", org_name="X", inviter="Y")
    assert "error" in r

def test_pending():
    invites = [{"status": "pending"}, {"status": "accepted"}, {"status": "pending"}]
    r = build_pending_invites(invites=invites)
    assert r["pending_count"] == 2
    assert r["accepted_count"] == 1
