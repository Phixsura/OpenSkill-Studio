from app.services.app_marketplace_app_invite_system import create_invite, accept_invite, list_pending_invites

def test_create():
    r = create_invite(app_id="a1", email="bob@example.com", role="developer", invited_by="u1")
    assert r["invite_id"].startswith("inv_")
    assert r["status"] == "pending"
    assert "invite/" in r["invite_url"]

def test_invalid_email():
    r = create_invite(app_id="a1", email="notanemail", role="developer", invited_by="u1")
    assert "error" in r

def test_accept():
    r = accept_invite(token="a" * 30, user_id="u2")
    assert r["success"]

def test_list():
    r = list_pending_invites(app_id="a1")
    assert r["total"] == 2
