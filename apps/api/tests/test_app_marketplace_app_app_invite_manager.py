from app.services.app_marketplace_app_app_invite_manager import create_invite, verify_invite_token

def test_create():
    r = create_invite(email="alice@example.com", role="editor", inviter="Bob")
    assert r["status"] == "pending"
    assert r["role"] == "editor"
    assert len(r["token"]) > 20

def test_verify():
    r = create_invite(email="a@b.com", role="admin", inviter="X")
    assert verify_invite_token(token=r["token"], signature=r["signature"])
    assert not verify_invite_token(token=r["token"], signature="bad_sig_0000000")

def test_invalid_email():
    r = create_invite(email="not-email", role="viewer", inviter="X")
    assert "error" in r

def test_invalid_role():
    r = create_invite(email="a@b.com", role="superadmin", inviter="X")
    assert "error" in r
